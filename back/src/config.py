"""
Configuration module for Doca
Loads environment variables from .env file and provides default configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Typesense configuration
TYPESENSE_HOST = os.getenv("DOCA_TYPESENSE_HOST", "http://localhost:8108")
TYPESENSE_API_KEY = os.getenv("DOCA_TYPESENSE_API_KEY", "xyz")
COLLECTION_NAME = os.getenv("DOCA_COLLECTION_NAME", "doca_documents")

# Chunking configuration
CHUNK_SIZE = int(os.getenv("DOCA_CHUNK_SIZE", "512"))  # Уменьшили с 512 до 256
CHUNK_OVERLAP = int(os.getenv("DOCA_CHUNK_OVERLAP", "128"))  # Уменьшили с 128 до 64

# Embedding model configuration
MODEL_NAME = os.getenv(
    "DOCA_MODEL_NAME", 
    "paraphrase-multilingual-MiniLM-L12-v2"  # Multilingual model with Russian support
)

# Memory optimization
USE_CUDA = os.getenv("DOCA_USE_CUDA", "0") == "1"
MEMORY_LIMIT = float(os.getenv("DOCA_MEMORY_LIMIT", "8.0"))  # in GB
BATCH_SIZE = int(os.getenv("DOCA_BATCH_SIZE", "2"))  # Уменьшили с 4 до 2
