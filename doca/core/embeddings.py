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

from doca import config


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
        
        # Show progress bar for larger datasets
        use_progress = len(chunks) > 10
        progress_bar = None
        if use_progress:
            progress_bar = tqdm(total=len(chunks), desc="Generating embeddings", unit="chunk")
        
        try:
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                batch_embeddings = self.model.encode(batch, show_progress_bar=False).tolist()
                all_embeddings.extend(batch_embeddings)
                
                # Update progress bar
                if progress_bar:
                    progress_bar.update(len(batch))
                
                # Force garbage collection to free memory after each batch
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                # Small delay to allow system to stabilize memory usage
                if i % (batch_size * 2) == 0 and i > 0:
                    time.sleep(0.1)
        finally:
            if progress_bar:
                progress_bar.close()
        
        return all_embeddings
