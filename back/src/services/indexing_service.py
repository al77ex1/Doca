"""
Indexing service for Doca backend
"""
import os
import asyncio
import gc
import logging
from pathlib import Path
from typing import Optional
import psutil

from src.core.indexer import DocumentIndexer
from src import config
from src.utils.es_health_check import wait_for_elasticsearch
from src.notifications.notifier import Notifier

# Configure logging
logger = logging.getLogger(__name__)

class IndexingService:
    """
    Service for document indexing operations
    """
    
    def __init__(self, notifier: Notifier, 
                 es_host: str = config.ES_HOST,
                 index_name: str = config.INDEX_NAME,
                 model_name: str = config.MODEL_NAME,
                 chunk_size: int = config.CHUNK_SIZE,
                 chunk_overlap: int = config.CHUNK_OVERLAP,
                 recreate_index: bool = True):
        """
        Initialize indexing service
        
        Args:
            notifier: Notification system
            es_host: Elasticsearch host
            index_name: Elasticsearch index name
            model_name: Embedding model name
            chunk_size: Text chunk size
            chunk_overlap: Text chunk overlap
            recreate_index: Whether to recreate the index
        """
        self.notifier = notifier
        self.es_host = es_host
        self.index_name = index_name
        self.model_name = model_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.recreate_index = recreate_index
        self.indexer = None
        
        # Set strict file size limit
        self.MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB limit per file
        self.BATCH_SIZE = 5  # Process 5 files at a time
    
    async def initialize(self):
        """
        Initialize the indexer
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Check Elasticsearch connection first
            await self.notifier.send_status('checking', 'Checking Elasticsearch connection...')
            
            if not wait_for_elasticsearch(self.es_host, max_retries=5, retry_interval=1):
                error_msg = f"Cannot connect to Elasticsearch at {self.es_host}. Please check if Elasticsearch is running."
                logger.error(error_msg)
                await self.notifier.send_error(error_msg)
                return False
            
            # Initialize indexer
            self.indexer = DocumentIndexer(
                es_host=self.es_host,
                index_name=self.index_name,
                model_name=self.model_name,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                recreate_index=self.recreate_index,
            )
            
            return True
        except Exception as e:
            error_msg = f"Error initializing indexer: {str(e)}"
            logger.error(error_msg)
            await self.notifier.send_error(error_msg)
            return False
    
    async def index_directory(self, directory_path: str, recursive: bool = True) -> int:
        """
        Index all supported files in a directory with progress reporting
        
        Args:
            directory_path: Path to the directory to index
            recursive: Whether to recursively search for files
            
        Returns:
            int: Number of chunks successfully indexed
        """
        if not self.indexer:
            if not await self.initialize():
                return 0
        
        indexed_count = 0
        skipped_count = 0
        error_count = 0
        
        try:
            # Force aggressive memory cleanup before starting
            self._cleanup_memory()
            
            # Get all supported files
            path = Path(directory_path)
            supported_extensions = list(self.indexer.parsers.keys())
            
            # Find all files with supported extensions
            all_files = []
            if recursive:
                for ext in supported_extensions:
                    all_files.extend(list(path.glob(f"**/*.{ext}")))
            else:
                for ext in supported_extensions:
                    all_files.extend(list(path.glob(f"*.{ext}")))
            
            # Sort files by size to process smaller files first
            all_files.sort(key=lambda p: p.stat().st_size)
            
            # Filter out files that are too large
            filtered_files = []
            for file_path in all_files:
                file_size = file_path.stat().st_size
                if file_size > self.MAX_FILE_SIZE:
                    skipped_count += 1
                    await self.notifier.send_warning(
                        f"File too large ({file_size} bytes). Skipping.",
                        str(file_path)
                    )
                else:
                    filtered_files.append(file_path)
            
            total_files = len(filtered_files)
            await self.notifier.send_indexing_started(total_files, skipped_count)
            
            # Process files in smaller batches to manage memory better
            for batch_idx in range(0, len(filtered_files), self.BATCH_SIZE):
                # Force aggressive memory cleanup between batches
                self._cleanup_memory()
                
                # Process a batch of files
                batch_files = filtered_files[batch_idx:batch_idx + self.BATCH_SIZE]
                
                for i, file_path in enumerate(batch_files):
                    try:
                        # Calculate overall progress
                        overall_idx = batch_idx + i
                        
                        # Get memory usage for monitoring
                        memory_usage_mb = self._get_memory_usage()
                        
                        await self.notifier.send_status(
                            'processing',
                            f"Processing file {overall_idx + 1}/{total_files}",
                        )
                        
                        # Index the file
                        file_chunks = self.indexer.index_file(str(file_path))
                        indexed_count += file_chunks
                        
                        # Send progress update
                        await self.notifier.send_progress(
                            overall_idx + 1,
                            total_files,
                            str(file_path),
                            file_chunks,
                            memory_usage_mb
                        )
                    except Exception as e:
                        error_count += 1
                        error_msg = f"Error processing file {file_path}: {str(e)}"
                        logger.error(error_msg)
                        await self.notifier.send_error(error_msg, str(file_path))
                    
                    # Force garbage collection after each file
                    gc.collect()
                    
                    # Small delay to prevent overwhelming the socket and allow memory cleanup
                    await asyncio.sleep(0.2)
                
                # Additional delay between batches to ensure memory is freed
                await asyncio.sleep(1.0)
            
            # Send completion event
            await self.notifier.send_indexing_completed(
                total_files,
                indexed_count,
                skipped_count,
                error_count
            )
            
            return indexed_count
        except Exception as e:
            error_msg = f"Error during indexing process: {str(e)}"
            logger.error(error_msg)
            await self.notifier.send_error(error_msg)
            return indexed_count
    
    def _cleanup_memory(self):
        """
        Perform aggressive memory cleanup
        """
        gc.collect()
        
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
    
    def _get_memory_usage(self) -> float:
        """
        Get current memory usage
        
        Returns:
            float: Memory usage in MB
        """
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        return memory_info.rss / 1024 / 1024

# Service factory
_indexing_service = None

def get_indexing_service(notifier: Notifier) -> IndexingService:
    """
    Get or create indexing service instance
    
    Args:
        notifier: Notification system
        
    Returns:
        IndexingService: Indexing service instance
    """
    global _indexing_service
    if _indexing_service is None:
        _indexing_service = IndexingService(notifier)
    return _indexing_service
