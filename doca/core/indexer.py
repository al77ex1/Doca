"""
Document Indexer for Doca
Coordinates the indexing process using parsers, chunking, embeddings, and storage
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Type
from tqdm import tqdm

from doca import config
from doca.parsers.base import BaseParser
from doca.parsers.markdown import MarkdownParser
from doca.utils.chunking import chunk_text
from doca.core.embeddings import EmbeddingGenerator
from doca.core.storage import ElasticsearchStorage


class DocumentIndexer:
    """Class for indexing documents with embeddings in Elasticsearch"""
    
    def __init__(
        self,
        es_host: str = config.ES_HOST,
        index_name: str = config.INDEX_NAME,
        model_name: str = config.MODEL_NAME,
        chunk_size: int = config.CHUNK_SIZE,
        chunk_overlap: int = config.CHUNK_OVERLAP,
    ):
        """
        Initialize the document indexer
        
        Args:
            es_host: Elasticsearch host URL
            index_name: Elasticsearch index name
            model_name: Sentence transformer model name
            chunk_size: Text chunk size in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize components
        self.embedding_generator = EmbeddingGenerator(model_name=model_name)
        self.storage = ElasticsearchStorage(es_host=es_host, index_name=index_name)
        
        # Update storage with embedding dimension
        self.storage.update_mapping(self.embedding_generator.embedding_dim)
        
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
            
            # Проверка размера файла перед чтением
            file_size = os.path.getsize(file_path)
            max_file_size = 50 * 1024 * 1024  # 50 МБ
            if file_size > max_file_size:
                print(f"Warning: File {file_path} is too large ({file_size} bytes). Skipping.")
                return 0
            
            # Read file content with error handling
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Попробуем другие кодировки
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
            
            # Очистка памяти
            gc.collect()
            
            # Parse content to plain text
            try:
                text = parser.parse(content)
                # Освобождаем память
                del content
                gc.collect()
            except Exception as e:
                print(f"Error parsing file {file_path}: {e}")
                return 0
            
            # Split into chunks
            try:
                chunks = chunk_text(text, self.chunk_size, self.chunk_overlap)
                # Освобождаем память
                del text
                gc.collect()
            except MemoryError:
                print(f"Memory error when chunking file {file_path}. Try reducing chunk size.")
                return 0
            except Exception as e:
                print(f"Error chunking file {file_path}: {e}")
                return 0
            
            # Проверка на пустой список чанков
            if not chunks:
                print(f"Warning: No chunks created for file {file_path}")
                return 0
                
            # Generate embeddings
            try:
                embeddings = self.embedding_generator.generate_embeddings(chunks)
            except Exception as e:
                print(f"Error generating embeddings for file {file_path}: {e}")
                return 0
            
            # Prepare documents for indexing
            documents = []
            try:
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    doc = self.storage.prepare_document(
                        file_path=file_path,
                        file_type=ext,
                        chunk_id=i,
                        content=chunk,
                        embedding=embedding,
                        metadata={"indexed_at": time.time()}
                    )
                    documents.append(doc)
                    
                # Освобождаем память
                del chunks
                del embeddings
                gc.collect()
            except Exception as e:
                print(f"Error preparing documents for file {file_path}: {e}")
                return 0
            
            # Index documents
            try:
                success, failed = self.storage.index_documents(documents)
                return success
            except Exception as e:
                print(f"Error indexing documents for file {file_path}: {e}")
                return 0
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
