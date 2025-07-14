"""
Elasticsearch adapter for Doca backend
"""
import logging
from typing import Dict, Any, List, Optional
from elasticsearch import Elasticsearch, exceptions as es_exceptions

# Configure logging
logger = logging.getLogger(__name__)

class ElasticsearchAdapter:
    """
    Adapter for Elasticsearch operations
    """
    
    def __init__(self, host: str, index_name: str):
        """
        Initialize Elasticsearch adapter
        
        Args:
            host: Elasticsearch host URL
            index_name: Index name to use
        """
        self.host = host
        self.index_name = index_name
        self.client = None
    
    def connect(self) -> bool:
        """
        Connect to Elasticsearch
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = Elasticsearch(self.host)
            if not self.client.ping():
                logger.error(f"Cannot connect to Elasticsearch at {self.host}")
                return False
            return True
        except es_exceptions.ConnectionError as e:
            logger.error(f"Elasticsearch connection error: {str(e)}")
            return False
    
    def create_index(self, mapping: Dict[str, Any], recreate: bool = False) -> bool:
        """
        Create Elasticsearch index with specified mapping
        
        Args:
            mapping: Index mapping
            recreate: Whether to recreate the index if it exists
            
        Returns:
            bool: True if index created successfully, False otherwise
        """
        if not self.client:
            if not self.connect():
                return False
        
        try:
            # Check if index exists
            if self.client.indices.exists(index=self.index_name):
                if recreate:
                    logger.info(f"Deleting existing index {self.index_name}")
                    self.client.indices.delete(index=self.index_name)
                else:
                    logger.info(f"Index {self.index_name} already exists")
                    return True
            
            # Create index with mapping
            logger.info(f"Creating index {self.index_name}")
            self.client.indices.create(index=self.index_name, body=mapping)
            return True
        except es_exceptions.ElasticsearchException as e:
            logger.error(f"Error creating index: {str(e)}")
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
                self.client.index(index=self.index_name, id=doc_id, body=document)
            else:
                self.client.index(index=self.index_name, body=document)
            return True
        except es_exceptions.ElasticsearchException as e:
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
            # Prepare bulk request body
            bulk_body = []
            for doc in documents:
                # Add index action
                bulk_body.append({"index": {"_index": self.index_name}})
                # Add document
                bulk_body.append(doc)
            
            # Execute bulk request
            response = self.client.bulk(body=bulk_body, refresh=True)
            
            # Count successful operations
            success_count = 0
            if not response.get("errors", True):
                success_count = len(documents)
            else:
                for item in response.get("items", []):
                    if "index" in item and item["index"].get("status") in (200, 201):
                        success_count += 1
            
            return success_count
        except es_exceptions.ElasticsearchException as e:
            logger.error(f"Error bulk indexing documents: {str(e)}")
            return 0
    
    def search(self, query: Dict[str, Any], size: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents
        
        Args:
            query: Elasticsearch query
            size: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: Search results
        """
        if not self.client:
            if not self.connect():
                return []
        
        try:
            response = self.client.search(index=self.index_name, body=query, size=size)
            return [hit["_source"] for hit in response["hits"]["hits"]]
        except es_exceptions.ElasticsearchException as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []
