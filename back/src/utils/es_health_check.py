"""
Elasticsearch health check utility
Provides functions to wait for Elasticsearch to be ready
"""

import time
import requests
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def wait_for_elasticsearch(es_host: str, max_retries: int = 30, retry_interval: int = 2) -> bool:
    """
    Wait for Elasticsearch to be ready to accept connections
    
    Args:
        es_host: Elasticsearch host URL
        max_retries: Maximum number of retries
        retry_interval: Interval between retries in seconds
        
    Returns:
        True if Elasticsearch is ready, False otherwise
    """
    # Parse the URL to get the base URL without path
    parsed_url = urlparse(es_host)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    logger.info(f"Waiting for Elasticsearch at {base_url}...")
    
    for i in range(max_retries):
        try:
            # Try to access the Elasticsearch health endpoint
            response = requests.get(f"{base_url}/_cluster/health", timeout=5)
            
            if response.status_code == 200:
                health_data = response.json()
                status = health_data.get("status")
                
                if status in ["green", "yellow"]:
                    logger.info(f"Elasticsearch is ready with status: {status}")
                    return True
                else:
                    logger.warning(f"Elasticsearch status is {status}, waiting...")
            else:
                logger.warning(f"Elasticsearch returned status code {response.status_code}, waiting...")
                
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection to Elasticsearch failed (attempt {i+1}/{max_retries}), retrying in {retry_interval} seconds...")
        except Exception as e:
            logger.warning(f"Error checking Elasticsearch health: {str(e)}, retrying...")
        
        time.sleep(retry_interval)
    
    logger.error(f"Failed to connect to Elasticsearch after {max_retries} attempts")
    return False
