"""
Storage module for Doca using Typesense
Handles interaction with Typesense for document storage and retrieval
"""

import time
import logging
from typing import List, Dict, Any, Tuple
import typesense
from typesense.exceptions import ObjectNotFound, RequestMalformed, ServerError

from src import config
from src.utils.typesense_health_check import wait_for_typesense

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TypesenseStorage:
    """Class for storing and retrieving documents in Typesense"""
    
    def __init__(self, host: str = config.TYPESENSE_HOST, api_key: str = config.TYPESENSE_API_KEY, 
                 collection_name: str = config.COLLECTION_NAME):
        """
        Initialize the Typesense storage
        
        Args:
            host: Typesense host URL
            api_key: Typesense API key
            collection_name: Name of the Typesense collection
        """
        self.host = host
        self.api_key = api_key
        self.collection_name = collection_name
        
        # Parse host to get components for Typesense client
        import re
        host_match = re.match(r'http://([^:]+):(\d+)', host)
        if host_match:
            self.host_name = host_match.group(1)
            self.port = host_match.group(2)
        else:
            self.host_name = host.replace('http://', '')
            self.port = "8108"  # Default Typesense port
        
        # Wait for Typesense to be ready before connecting
        if not wait_for_typesense(self.host, self.api_key):
            logger.error(f"Failed to connect to Typesense at {host}. Please check if Typesense is running.")
            raise ConnectionError(f"Could not connect to Typesense at {host}")
            
        # Connect to Typesense
        self.client = typesense.Client({
            'api_key': self.api_key,
            'nodes': [{
                'host': self.host_name,
                'port': self.port,
                'protocol': 'http'
            }],
            'connection_timeout_seconds': 2
        })
        
        # Create collection if it doesn't exist
        self._create_collection()
    
    def _create_collection(self, embedding_dim: int = None) -> None:
        """
        Create Typesense collection with appropriate schema for vector search
        
        Args:
            embedding_dim: Dimension of embeddings (if None, will be set later)
        """
        try:
            # Check if collection exists
            collections = self.client.collections.retrieve()
            collection_exists = any(c['name'] == self.collection_name for c in collections)
            
            if not collection_exists:
                print(f"Creating collection: {self.collection_name}")
                
                # Define collection schema with vector field for embeddings
                schema = {
                    'name': self.collection_name,
                    'fields': [
                        {'name': 'content', 'type': 'string'},
                        {'name': 'content_vector', 'type': 'float[]', 'num_dim': embedding_dim if embedding_dim else 384},
                        {'name': 'file_path', 'type': 'string', 'facet': True},
                        {'name': 'file_name', 'type': 'string', 'facet': True},
                        {'name': 'chunk_id', 'type': 'int32'},
                        {'name': 'file_type', 'type': 'string', 'facet': True},
                        {'name': 'metadata', 'type': 'object'}
                    ],
                    'default_sorting_field': 'chunk_id',
                    'enable_nested_fields': True
                }
                
                # Create the collection
                self.client.collections.create(schema)
                print(f"Collection created: {self.collection_name}")
            else:
                print(f"Collection already exists: {self.collection_name}")
                
        except (ObjectNotFound, RequestMalformed, ServerError, Exception) as e:
            print(f"Error creating collection: {e}")
            
    def delete_collection(self) -> bool:
        """
        Delete the Typesense collection if it exists
        
        Returns:
            True if collection was deleted, False otherwise
        """
        try:
            collections = self.client.collections.retrieve()
            collection_exists = any(c['name'] == self.collection_name for c in collections)
            
            if collection_exists:
                self.client.collections[self.collection_name].delete()
                print(f"Collection deleted: {self.collection_name}")
                return True
            else:
                print(f"Collection does not exist: {self.collection_name}")
                return False
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False
            
    def recreate_collection(self, embedding_dim: int) -> bool:
        """
        Delete and recreate the collection with the correct embedding dimension
        
        Args:
            embedding_dim: Dimension of embeddings
            
        Returns:
            True if collection was recreated successfully, False otherwise
        """
        try:
            # Delete existing collection
            self.delete_collection()
            
            # Define collection schema with vector field for embeddings
            schema = {
                'name': self.collection_name,
                'fields': [
                    {'name': 'content', 'type': 'string'},
                    {'name': 'content_vector', 'type': 'float[]', 'num_dim': embedding_dim},
                    {'name': 'file_path', 'type': 'string', 'facet': True},
                    {'name': 'file_name', 'type': 'string', 'facet': True},
                    {'name': 'chunk_id', 'type': 'int32'},
                    {'name': 'file_type', 'type': 'string', 'facet': True},
                    {'name': 'metadata', 'type': 'object'}
                ],
                'default_sorting_field': 'chunk_id',
                'enable_nested_fields': True
            }
            
            # Create the collection
            self.client.collections.create(schema)
            print(f"Collection recreated: {self.collection_name}")
            return True
        except Exception as e:
            print(f"Error recreating collection: {e}")
            return False
    
    def update_schema(self, embedding_dim: int) -> None:
        """
        Update collection schema with correct embedding dimension
        
        Args:
            embedding_dim: Dimension of embeddings
        """
        # Typesense doesn't support updating schema dimensions after creation
        # We need to recreate the collection
        try:
            collection = self.client.collections[self.collection_name].retrieve()
            
            # Check if the vector dimension matches
            for field in collection['fields']:
                if field['name'] == 'content_vector':
                    if field.get('num_dim') != embedding_dim:
                        print(f"Warning: Collection exists with dimension {field.get('num_dim')}, but model uses {embedding_dim}")
                        print("Recreating collection with correct dimension...")
                        self.recreate_collection(embedding_dim)
                    break
        except Exception as e:
            print(f"Error checking schema: {e}")
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        Index multiple documents in Typesense
        
        Args:
            documents: List of document dictionaries to index
            
        Returns:
            Tuple of (success_count, failed_count)
        """
        try:
            # Prepare documents for Typesense
            typesense_docs = []
            for doc in documents:
                # Extract the document source
                source = doc.get('_source', doc)
                
                # Create a new document with the required format for Typesense
                # Ensure metadata is a simple dictionary without nested objects
                metadata = source.get('metadata', {})
                if isinstance(metadata, dict):
                    # Convert any non-string values to strings to avoid object type issues
                    for key, value in metadata.items():
                        if not isinstance(value, (str, int, float, bool)):
                            metadata[key] = str(value)
                else:
                    metadata = {'indexed_at': str(time.time())}
                
                typesense_doc = {
                    'id': doc.get('_id', f"{source['file_path']}_{source['chunk_id']}"),
                    'content': source['content'],
                    'content_vector': source['content_vector'],
                    'file_path': source['file_path'],
                    'file_name': source['file_name'],
                    'chunk_id': source['chunk_id'],
                    'file_type': source['file_type'],
                    'metadata': metadata
                }
                typesense_docs.append(typesense_doc)
            
            # Import documents
            results = self.client.collections[self.collection_name].documents.import_(typesense_docs)
            
            # Count successes and failures
            success_count = sum(1 for r in results if r.get('success', False))
            failed_count = len(documents) - success_count
            
            return success_count, failed_count
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
        Prepare a document for Typesense indexing
        
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
        
        # For compatibility with the ElasticsearchStorage format
        return {
            "_index": self.collection_name,
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
