"""
API routes for Doca backend
"""
from fastapi import APIRouter, Depends
from src import config
from src.services.indexing_service import get_indexing_service

# Create router
router = APIRouter()

@router.get("/")
async def root():
    """
    Root endpoint
    
    Returns:
        dict: Welcome message
    """
    return {"message": "Welcome to Doca API"}

@router.get("/config")
async def get_config():
    """
    Get current configuration
    
    Returns:
        dict: Configuration parameters
    """
    return {
        "typesense_host": config.TYPESENSE_HOST,
        "collection_name": config.COLLECTION_NAME,
        "model_name": config.MODEL_NAME,
        "chunk_size": config.CHUNK_SIZE,
        "chunk_overlap": config.CHUNK_OVERLAP,
    }
