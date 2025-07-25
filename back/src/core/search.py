"""
Search module for Doca using Typesense
"""

import logging
from typing import List, Dict, Any, Optional
import typesense
from typesense.exceptions import ObjectNotFound, RequestMalformed, ServerError

from src import config

# Configure logging
logger = logging.getLogger(__name__)

class TypesenseSearch:
    """Class for searching documents in Typesense"""
    
    def __init__(self, host: str = config.TYPESENSE_HOST, api_key: str = config.TYPESENSE_API_KEY, 
                 collection_name: str = config.COLLECTION_NAME):
        """
        Initialize the Typesense search
        
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
    
    def search_by_text(self, query_text: str, limit: int = 10, filter_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search documents by text query
        
        Args:
            query_text: Text to search for
            limit: Maximum number of results to return
            filter_by: Optional filter expression
            
        Returns:
            List of matching documents
        """
        try:
            search_params = {
                'q': query_text,
                'query_by': 'content',
                'limit': limit
            }
            
            if filter_by:
                search_params['filter_by'] = filter_by
            
            results = self.client.collections[self.collection_name].documents.search(search_params)
            
            # Extract hits
            hits = []
            for hit in results['hits']:
                document = hit['document']
                document['score'] = hit['text_match']  # Add score to document
                hits.append(document)
            
            return hits
        except (ObjectNotFound, RequestMalformed, ServerError, Exception) as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []
    
    def search_by_vector(self, vector: List[float], limit: int = 10, filter_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search documents by vector similarity
        
        Args:
            vector: Embedding vector to search with
            limit: Maximum number of results to return
            filter_by: Optional filter expression
            
        Returns:
            List of matching documents
        """
        try:
            search_params = {
                'vector_query': f'content_vector:({",".join(map(str, vector))})',
                'limit': limit
            }
            
            if filter_by:
                search_params['filter_by'] = filter_by
            
            results = self.client.collections[self.collection_name].documents.search(search_params)
            
            # Extract hits
            hits = []
            for hit in results['hits']:
                document = hit['document']
                document['score'] = hit['vector_distance']  # Add score to document
                hits.append(document)
            
            return hits
        except (ObjectNotFound, RequestMalformed, ServerError, Exception) as e:
            logger.error(f"Error searching documents by vector: {str(e)}")
            return []
    
    def hybrid_search(self, query_text: str, vector: List[float], limit: int = 10, 
                      filter_by: Optional[str] = None, text_weight: float = 0.3) -> List[Dict[str, Any]]:
        """
        Perform hybrid search using both text and vector similarity
        
        Args:
            query_text: Text to search for
            vector: Embedding vector to search with
            limit: Maximum number of results to return
            filter_by: Optional filter expression
            text_weight: Weight to give to text search (0-1), rest goes to vector search
            
        Returns:
            List of matching documents
        """
        try:
            search_params = {
                'q': query_text,
                'query_by': 'content',
                'vector_query': f'content_vector:({",".join(map(str, vector))})',
                'limit': limit,
                'text_match_weight': text_weight,
                'vector_match_weight': 1.0 - text_weight
            }
            
            if filter_by:
                search_params['filter_by'] = filter_by
            
            results = self.client.collections[self.collection_name].documents.search(search_params)
            
            # Extract hits
            hits = []
            for hit in results['hits']:
                document = hit['document']
                document['score'] = hit.get('hybrid_score', 0.0)  # Add score to document
                hits.append(document)
            
            return hits
        except (ObjectNotFound, RequestMalformed, ServerError, Exception) as e:
            logger.error(f"Error performing hybrid search: {str(e)}")
            return []
