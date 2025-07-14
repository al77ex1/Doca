"""
Storage module for Doca
Handles interaction with Elasticsearch for document storage and retrieval
"""

import time
from typing import List, Dict, Any, Tuple
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from doca import config


class ElasticsearchStorage:
    """Class for storing and retrieving documents in Elasticsearch"""
    
    def __init__(self, es_host: str = config.ES_HOST, index_name: str = config.INDEX_NAME):
        """
        Initialize the Elasticsearch storage
        
        Args:
            es_host: Elasticsearch host URL
            index_name: Name of the Elasticsearch index
        """
        self.es_host = es_host
        self.index_name = index_name
        
        # Connect to Elasticsearch
        self.es = Elasticsearch(es_host)
        
        # Create index if it doesn't exist
        self._create_index()
    
    def _create_index(self, embedding_dim: int = None) -> None:
        """
        Create Elasticsearch index with appropriate mappings for vector search
        
        Args:
            embedding_dim: Dimension of embeddings (if None, will be set later)
        """
        if not self.es.indices.exists(index=self.index_name):
            print(f"Creating index: {self.index_name}")
            
            # Define index mapping with vector field for embeddings
            mapping = {
                "mappings": {
                    "properties": {
                        "content": {"type": "text"},
                        "content_vector": {
                            "type": "dense_vector",
                            "dims": embedding_dim if embedding_dim else 384,  # Default dim, will be updated if needed
                            "index": True,
                            "similarity": "cosine"
                        },
                        "file_path": {"type": "keyword"},
                        "file_name": {"type": "keyword"},
                        "chunk_id": {"type": "integer"},
                        "file_type": {"type": "keyword"},  # Added file type for filtering
                        "metadata": {"type": "object"}
                    }
                }
            }
            
            # Create the index
            self.es.indices.create(index=self.index_name, body=mapping)
            print(f"Index created: {self.index_name}")
        else:
            print(f"Index already exists: {self.index_name}")
    
    def update_mapping(self, embedding_dim: int) -> None:
        """
        Update index mapping with correct embedding dimension
        
        Args:
            embedding_dim: Dimension of embeddings
        """
        # This is a simplified implementation - in production, you'd need
        # to handle the case where the index already exists with a different dimension
        if self.es.indices.exists(index=self.index_name):
            try:
                mapping = self.es.indices.get_mapping(index=self.index_name)
                current_dim = mapping[self.index_name]["mappings"]["properties"]["content_vector"].get("dims")
                
                if current_dim != embedding_dim:
                    print(f"Warning: Index exists with dimension {current_dim}, but model uses {embedding_dim}")
                    # In a real implementation, you might want to reindex or handle this differently
            except Exception as e:
                print(f"Error checking mapping: {e}")
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        Index multiple documents in Elasticsearch
        
        Args:
            documents: List of document dictionaries to index
            
        Returns:
            Tuple of (success_count, failed_count)
        """
        try:
            success, failed = bulk(self.es, documents)
            return success, failed
        except Exception as e:
            print(f"Error indexing documents: {e}")
            return 0, len(documents)
    
    def prepare_document(
        self, 
        file_path: str,
        file_type: str,
        chunk_id: int,
        content: str, 
        embedding: List[float],
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Prepare a document for Elasticsearch indexing
        
        Args:
            file_path: Path to the source file
            file_type: Type of the file (e.g., 'markdown', 'text')
            chunk_id: ID of the chunk within the file
            content: Text content of the chunk
            embedding: Vector embedding of the content
            metadata: Additional metadata to store
            
        Returns:
            Document dictionary ready for indexing
        """
        if metadata is None:
            metadata = {}
        
        # Add timestamp if not present
        if "indexed_at" not in metadata:
            metadata["indexed_at"] = time.time()
        
        # Extract file name from path
        import os
        file_name = os.path.basename(file_path)
        
        return {
            "_index": self.index_name,
            "_id": f"{file_path}_{chunk_id}",
            "_source": {
                "content": content,
                "content_vector": embedding,
                "file_path": file_path,
                "file_name": file_name,
                "file_type": file_type,
                "chunk_id": chunk_id,
                "metadata": metadata
            }
        }
