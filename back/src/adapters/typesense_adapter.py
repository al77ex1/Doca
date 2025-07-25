"""
Typesense adapter for Doca backend
"""
import logging
from typing import Dict, Any, List, Optional
import typesense
from typesense.exceptions import ObjectNotFound, RequestMalformed, ServerError

# Configure logging
logger = logging.getLogger(__name__)

class TypesenseAdapter:
    """
    Adapter for Typesense operations
    """
    
    def __init__(self, host: str, api_key: str, collection_name: str):
        """
        Initialize Typesense adapter
        
        Args:
            host: Typesense host URL (without http:// prefix)
            api_key: Typesense API key
            collection_name: Collection name to use
        """
        self.host = host
        self.api_key = api_key
        self.collection_name = collection_name
        self.client = None
        
        # Parse host to get components for Typesense client
        import re
        host_match = re.match(r'http://([^:]+):(\d+)', host)
        if host_match:
            self.host_name = host_match.group(1)
            self.port = host_match.group(2)
        else:
            self.host_name = host
            self.port = "8108"  # Default Typesense port
    
    def connect(self) -> bool:
        """
        Connect to Typesense
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = typesense.Client({
                'api_key': self.api_key,
                'nodes': [{
                    'host': self.host_name,
                    'port': self.port,
                    'protocol': 'http'
                }],
                'connection_timeout_seconds': 2
            })
            
            # Check connection by retrieving health
            health = self.client.health.retrieve()
            if health['status'] == 'ok':
                return True
            else:
                logger.error(f"Typesense health check failed: {health}")
                return False
        except Exception as e:
            logger.error(f"Typesense connection error: {str(e)}")
            return False
    
    def create_collection(self, schema: Dict[str, Any], recreate: bool = False) -> bool:
        """
        Create Typesense collection with specified schema
        
        Args:
            schema: Collection schema
            recreate: Whether to recreate the collection if it exists
            
        Returns:
            bool: True if collection created successfully, False otherwise
        """
        if not self.client:
            if not self.connect():
                return False
        
        try:
            # Check if collection exists
            collections = self.client.collections.retrieve()
            collection_exists = any(c['name'] == self.collection_name for c in collections)
            
            if collection_exists:
                if recreate:
                    logger.info(f"Deleting existing collection {self.collection_name}")
                    self.client.collections[self.collection_name].delete()
                else:
                    logger.info(f"Collection {self.collection_name} already exists")
                    return True
            
            # Create collection with schema
            logger.info(f"Creating collection {self.collection_name}")
            self.client.collections.create(schema)
            return True
        except (ObjectNotFound, RequestMalformed, ServerError, Exception) as e:
            logger.error(f"Error creating collection: {str(e)}")
            return False
    
    def index_document(self, document: Dict[str, Any], doc_id: Optional[str] = None) -> bool:
        """
        Index a document
        
        Args:
            document: Document to index
            doc_id: Optional document ID
            
        Returns:
            bool: True if document indexed successfully, False otherwise
        """
        if not self.client:
            if not self.connect():
                return False
        
        try:
            if doc_id:
                document['id'] = doc_id
            
            self.client.collections[self.collection_name].documents.create(document)
            return True
        except (ObjectNotFound, RequestMalformed, ServerError, Exception) as e:
            logger.error(f"Error indexing document: {str(e)}")
            return False
    
    def bulk_index(self, documents: List[Dict[str, Any]]) -> int:
        """
        Bulk index multiple documents
        
        Args:
            documents: List of documents to index
            
        Returns:
            int: Number of documents successfully indexed
        """
        if not self.client:
            if not self.connect():
                return 0
        
        if not documents:
            return 0
        
        try:
            # Ensure each document has an ID
            for i, doc in enumerate(documents):
                if 'id' not in doc:
                    doc['id'] = str(i)
            
            # Execute bulk import
            result = self.client.collections[self.collection_name].documents.import_(documents)
            
            # Count successful operations
            success_count = 0
            for item in result:
                if item.get('success'):
                    success_count += 1
            
            return success_count
        except (ObjectNotFound, RequestMalformed, ServerError, Exception) as e:
            logger.error(f"Error bulk indexing documents: {str(e)}")
            return 0
    
    def search(self, query_params: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents
        
        Args:
            query_params: Typesense search parameters
            limit: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: Search results
        """
        if not self.client:
            if not self.connect():
                return []
        
        try:
            # Add limit to query parameters
            query_params['limit'] = limit
            
            # Execute search
            search_results = self.client.collections[self.collection_name].documents.search(query_params)
            
            # Extract hits
            return [hit['document'] for hit in search_results['hits']]
        except (ObjectNotFound, RequestMalformed, ServerError, Exception) as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []
