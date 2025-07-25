"""
Document Indexer for Doca
Coordinates the indexing process using parsers, chunking, embeddings, and storage
"""

import os
import time
import gc
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Type
from tqdm import tqdm

from src import config
from src.parsers.base import BaseParser
from src.parsers.markdown import MarkdownParser
from src.utils.chunking import chunk_text
from src.core.embeddings import EmbeddingGenerator
from src.core.typesense_storage import TypesenseStorage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DocumentIndexer:
    """Class for indexing documents with embeddings in Typesense"""
    
    def __init__(
        self,
        typesense_host: str = config.TYPESENSE_HOST,
        typesense_api_key: str = config.TYPESENSE_API_KEY,
        collection_name: str = config.COLLECTION_NAME,
        model_name: str = config.MODEL_NAME,
        chunk_size: int = config.CHUNK_SIZE,
        chunk_overlap: int = config.CHUNK_OVERLAP,
        recreate_collection: bool = False,
    ):
        """
        Initialize the document indexer
        
        Args:
            typesense_host: Typesense host URL
            typesense_api_key: Typesense API key
            collection_name: Typesense collection name
            model_name: Sentence transformer model name
            chunk_size: Text chunk size in characters
            chunk_overlap: Overlap between chunks in characters
            recreate_index: Whether to recreate the index if it already exists
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize embedding generator
        self.embedding_generator = EmbeddingGenerator(model_name=model_name)
        
        # Initialize storage with error handling
        try:
            self.storage = TypesenseStorage(host=typesense_host, api_key=typesense_api_key, collection_name=collection_name)
            
            # Recreate collection if requested
            if recreate_collection:
                logger.info("Recreating collection...")
                self.storage.recreate_collection(self.embedding_generator.embedding_dim)
            else:
                # Update storage with embedding dimension
                self.storage.update_schema(self.embedding_generator.embedding_dim)
        except ConnectionError as e:
            logger.error(f"Failed to connect to Typesense: {str(e)}")
            raise ConnectionError(f"Failed to connect to Typesense at {typesense_host}. Please check if Typesense is running.") from e
        except Exception as e:
            logger.error(f"Error initializing storage: {str(e)}")
            raise
        
        # Register parsers
        self.parsers: Dict[str, Type[BaseParser]] = {}
        self._register_parsers()
    
    def _register_parsers(self) -> None:
        """Register all available parsers"""
        # Register Markdown parser
        parser = MarkdownParser()
        for ext in parser.get_supported_extensions():
            self.parsers[ext] = MarkdownParser
        
        # Additional parsers can be registered here
        # For example:
        # from doca.parsers.html import HtmlParser
        # parser = HtmlParser()
        # for ext in parser.get_supported_extensions():
        #     self.parsers[ext] = HtmlParser
    
    def _get_parser_for_file(self, file_path: str) -> Optional[BaseParser]:
        """
        Get appropriate parser for a file based on its extension
        
        Args:
            file_path: Path to the file
            
        Returns:
            Parser instance or None if no parser is available
        """
        ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        parser_class = self.parsers.get(ext)
        
        if parser_class:
            return parser_class()
        
        return None
    
    def index_file(self, file_path: str) -> int:
        """
        Index a single file
        
        Args:
            file_path: Path to the file to index
            
        Returns:
            Number of chunks successfully indexed
        """
        try:
            # Get appropriate parser for the file
            parser = self._get_parser_for_file(file_path)
            if not parser:
                print(f"No parser available for file: {file_path}")
                return 0
            
            # Get file type
            ext = os.path.splitext(file_path)[1].lower().lstrip('.')
            
            # Strict file size check
            file_size = os.path.getsize(file_path)
            max_file_size = 5 * 1024 * 1024  # 5 MB - much stricter limit
            if file_size > max_file_size:
                print(f"Warning: File {file_path} is too large ({file_size} bytes). Skipping.")
                return 0
            
            # Read file content with error handling - using a context manager to ensure file is closed
            content = None
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try alternative encodings
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                    print(f"Note: File {file_path} opened with latin-1 encoding")
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
                    return 0
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                return 0
            
            if not content or len(content) == 0:
                print(f"Warning: Empty file {file_path}. Skipping.")
                return 0
                
            # Limit content size to prevent memory issues
            from src import config
            if len(content) > config.MAX_CONTENT_LENGTH:
                print(f"Warning: Content of {file_path} is too large ({len(content)} chars). Truncating to {config.MAX_CONTENT_LENGTH} chars.")
                content = content[:config.MAX_CONTENT_LENGTH]
            
            # Force garbage collection
            gc.collect()
            
            # Parse content to plain text
            try:
                text = parser.parse(content)
                # Free memory immediately
                del content
                gc.collect()
            except Exception as e:
                print(f"Error parsing file {file_path}: {e}")
                del content
                gc.collect()
                return 0
            
            # Split into chunks with configurable chunk size for memory efficiency
            try:
                # Use configurable chunk size from config
                from src import config
                effective_chunk_size = min(self.chunk_size, config.EFFECTIVE_CHUNK_SIZE)
                effective_overlap = min(self.chunk_overlap, config.EFFECTIVE_CHUNK_OVERLAP)
                
                print(f"Chunking text with size {effective_chunk_size} and overlap {effective_overlap}")
                chunks = chunk_text(text, effective_chunk_size, effective_overlap)
                # Free memory immediately
                del text
                gc.collect()
            except MemoryError:
                print(f"Memory error when chunking file {file_path}. Skipping.")
                return 0
            except Exception as e:
                print(f"Error chunking file {file_path}: {e}")
                return 0
            
            # Check for empty chunks
            if not chunks:
                print(f"Warning: No chunks created for file {file_path}")
                return 0
            
            # Limit number of chunks to prevent memory issues
            from src import config
            if len(chunks) > config.MAX_CHUNKS_PER_FILE:
                print(f"Warning: Too many chunks ({len(chunks)}) for file {file_path}. Limiting to {config.MAX_CHUNKS_PER_FILE}.")
                chunks = chunks[:config.MAX_CHUNKS_PER_FILE]
                
            # Generate embeddings and index in larger batches
            success_count = 0
            try:
                # Use config batch size for more efficient processing
                from src import config
                micro_batch_size = config.BATCH_SIZE
                
                # Process all chunks at once for embedding generation
                print(f"Generating embeddings for {len(chunks)} chunks...")
                all_embeddings = self.embedding_generator.generate_embeddings(chunks)
                
                # Prepare all documents
                print(f"Preparing {len(chunks)} documents for indexing...")
                all_documents = []
                for i, (chunk, embedding) in enumerate(zip(chunks, all_embeddings)):
                    doc = self.storage.prepare_document(
                        file_path=file_path,
                        file_type=ext,
                        chunk_id=i,
                        content=chunk,
                        embedding=embedding,
                        metadata={"indexed_at": time.time()}
                    )
                    all_documents.append(doc)
                
                # Index documents in batches
                print(f"Indexing {len(all_documents)} documents in batches of {micro_batch_size}...")
                success, failed = self.storage.index_documents(all_documents, batch_size=micro_batch_size)
                success_count = success
                
                # Free memory
                del chunks
                del all_embeddings
                del all_documents
                gc.collect()
                
                return success_count
            except Exception as e:
                print(f"Error processing chunks for file {file_path}: {e}")
                return success_count  # Return any successful chunks so far
        except MemoryError:
            print(f"Memory error when processing file {file_path}. Try increasing available memory.")
            return 0
        except Exception as e:
            print(f"Error indexing file {file_path}: {e}")
            return 0
    
    def index_directory(self, directory_path: str, recursive: bool = True) -> int:
        """
        Index all supported files in a directory
        
        Args:
            directory_path: Path to the directory to index
            recursive: Whether to recursively search for files
            
        Returns:
            Number of chunks successfully indexed
        """
        indexed_count = 0
        
        # Get all supported files
        path = Path(directory_path)
        supported_extensions = list(self.parsers.keys())
        
        # Find all files with supported extensions
        all_files = []
        if recursive:
            for ext in supported_extensions:
                all_files.extend(list(path.glob(f"**/*.{ext}")))
        else:
            for ext in supported_extensions:
                all_files.extend(list(path.glob(f"*.{ext}")))
        
        print(f"Found {len(all_files)} supported files in {directory_path}")
        
        # Index each file with progress bar
        for file_path in tqdm(all_files, desc="Indexing files"):
            indexed_count += self.index_file(str(file_path))
        
        return indexed_count
