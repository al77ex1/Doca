"""
Utility for checking Typesense health and waiting for it to be ready
"""

import time
import logging
import requests
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

def check_typesense_health(host: str, api_key: str) -> bool:
    """
    Check if Typesense is healthy
    
    Args:
        host: Typesense host URL
        api_key: Typesense API key
        
    Returns:
        bool: True if Typesense is healthy, False otherwise
    """
    try:
        # Ensure host has proper format
        if not host.startswith('http://') and not host.startswith('https://'):
            host = f"http://{host}"
        
        # Make health check request
        health_url = f"{host}/health"
        headers = {"X-TYPESENSE-API-KEY": api_key}
        
        response = requests.get(health_url, headers=headers, timeout=2)
        
        if response.status_code == 200:
            health_data = response.json()
            return health_data.get('ok', False)
        
        return False
    except Exception as e:
        logger.error(f"Error checking Typesense health: {str(e)}")
        return False

def wait_for_typesense(host: str, api_key: str, max_retries: int = 30, retry_interval: int = 2) -> bool:
    """
    Wait for Typesense to be ready
    
    Args:
        host: Typesense host URL
        api_key: Typesense API key
        max_retries: Maximum number of retries
        retry_interval: Interval between retries in seconds
        
    Returns:
        bool: True if Typesense is ready, False if max retries reached
    """
    logger.info(f"Waiting for Typesense at {host} to be ready...")
    
    for i in range(max_retries):
        if check_typesense_health(host, api_key):
            logger.info(f"Typesense at {host} is ready!")
            return True
        
        logger.info(f"Typesense not ready yet. Retry {i+1}/{max_retries}...")
        time.sleep(retry_interval)
    
    logger.error(f"Typesense at {host} is not ready after {max_retries} retries")
    return False
