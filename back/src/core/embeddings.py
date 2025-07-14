"""
Embeddings generation module for Doca
Handles loading models and generating embeddings with memory optimization
"""

import gc
import time
from typing import List
import torch
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

from src import config


class EmbeddingGenerator:
    """Class for generating embeddings from text chunks"""
    
    def __init__(self, model_name: str = config.MODEL_NAME):
        """
        Initialize the embedding generator
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        
        # Determine device (CPU/GPU)
        device = "cpu"  # Default to CPU for stability
        try:
            # Try to use CUDA if available and requested
            if torch.cuda.is_available() and config.USE_CUDA:
                device = "cuda"
                print("Using CUDA for embeddings")
        except Exception as e:
            print(f"Error checking CUDA: {e}, falling back to CPU")
        
        # Load the model
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name, device=device)
        
        # Get embedding dimension
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def generate_embeddings(self, chunks: List[str], batch_size: int = config.BATCH_SIZE) -> List[List[float]]:
        """
        Generate embeddings for text chunks with memory optimization
        
        Args:
            chunks: List of text chunks to generate embeddings for
            batch_size: Batch size for processing chunks
            
        Returns:
            List of embeddings (as lists of floats)
        """
        all_embeddings = []
        
        # Уменьшаем размер батча, если чанков слишком много
        if len(chunks) > 100 and batch_size > 2:
            batch_size = 2
            print(f"Reducing batch size to {batch_size} due to large number of chunks")
        
        # Show progress bar for larger datasets
        use_progress = len(chunks) > 10
        progress_bar = None
        if use_progress:
            progress_bar = tqdm(total=len(chunks), desc="Generating embeddings", unit="chunk")
        
        try:
            for i in range(0, len(chunks), batch_size):
                # Принудительная очистка памяти перед каждым батчем
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                try:
                    batch = chunks[i:i+batch_size]
                    # Используем более низкоуровневый API для большего контроля над памятью
                    with torch.no_grad():  # Отключаем вычисление градиентов для экономии памяти
                        batch_embeddings = self.model.encode(batch, show_progress_bar=False, convert_to_numpy=True).tolist()
                    all_embeddings.extend(batch_embeddings)
                    
                    # Явно удаляем переменные для освобождения памяти
                    del batch
                except Exception as e:
                    print(f"Error encoding batch {i}-{i+batch_size}: {e}")
                    # В случае ошибки добавляем нулевые эмбеддинги, чтобы сохранить структуру
                    for _ in range(min(batch_size, len(chunks) - i)):
                        all_embeddings.append([0.0] * self.embedding_dim)
                
                # Update progress bar
                if progress_bar:
                    progress_bar.update(min(batch_size, len(chunks) - i))
                
                # Force garbage collection to free memory after each batch
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                # Увеличиваем задержку для лучшей стабилизации памяти
                time.sleep(0.2)
        finally:
            if progress_bar:
                progress_bar.close()
            
            # Финальная очистка памяти
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        
        return all_embeddings
