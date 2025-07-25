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
CHUNK_SIZE = int(os.getenv("DOCA_CHUNK_SIZE", "512"))  # Стандартный размер чанка
CHUNK_OVERLAP = int(os.getenv("DOCA_CHUNK_OVERLAP", "128"))  # Стандартное перекрытие чанков

# Embedding model configuration
MODEL_NAME = os.getenv(
    "DOCA_MODEL_NAME", 
    "paraphrase-multilingual-MiniLM-L12-v2"  # Multilingual model with Russian support
)

# Memory optimization
USE_CUDA = os.getenv("DOCA_USE_CUDA", "0") == "1"
MEMORY_LIMIT = float(os.getenv("DOCA_MEMORY_LIMIT", "8.0"))  # in GB
BATCH_SIZE = int(os.getenv("DOCA_BATCH_SIZE", "50"))  # 50 для ускорения индексации

# File processing limits
MAX_CONTENT_LENGTH = int(os.getenv("DOCA_MAX_CONTENT_LENGTH", "100000"))  # 100K символов
MAX_CHUNKS_PER_FILE = int(os.getenv("DOCA_MAX_CHUNKS_PER_FILE", "50"))  # Максимум чанков на файл
EFFECTIVE_CHUNK_SIZE = int(os.getenv("DOCA_EFFECTIVE_CHUNK_SIZE", "512"))  # Размер чанка для больших файлов
EFFECTIVE_CHUNK_OVERLAP = int(os.getenv("DOCA_EFFECTIVE_CHUNK_OVERLAP", "128"))  # Перекрытие чанков
