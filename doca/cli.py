"""
Command-line interface for Doca
Handles command-line arguments and launches the indexer
"""

import argparse
import os
import time

from doca import config
from doca.core.indexer import DocumentIndexer


def main():
    """Main function to run the indexer from command line"""
    parser = argparse.ArgumentParser(description="Index documents for semantic search")
    parser.add_argument("directory", help="Directory containing documents to index")
    parser.add_argument("--es-host", default=config.ES_HOST, help="Elasticsearch host URL")
    parser.add_argument("--index-name", default=config.INDEX_NAME, help="Elasticsearch index name")
    parser.add_argument("--model", default=config.MODEL_NAME, help="Sentence transformer model name")
    parser.add_argument("--chunk-size", type=int, default=config.CHUNK_SIZE, help="Text chunk size in characters")
    parser.add_argument("--chunk-overlap", type=int, default=config.CHUNK_OVERLAP, help="Overlap between chunks in characters")
    parser.add_argument("--no-recursive", action="store_true", help="Don't recursively search for files")
    parser.add_argument("--use-cuda", action="store_true", help="Use CUDA for embeddings if available")
    parser.add_argument("--memory-limit", type=float, default=config.MEMORY_LIMIT, help="Limit memory usage in GB (if supported)")
    parser.add_argument("--batch-size", type=int, default=config.BATCH_SIZE, help="Batch size for embedding generation")
    
    args = parser.parse_args()
    
    # Set environment variables for memory management
    if args.use_cuda:
        os.environ["DOCA_USE_CUDA"] = "1"
    else:
        os.environ["DOCA_USE_CUDA"] = "0"
    
    # Try to limit memory usage if requested
    if args.memory_limit:
        try:
            import resource
            # Convert GB to bytes
            memory_limit_bytes = int(args.memory_limit * 1024 * 1024 * 1024)
            resource.setrlimit(resource.RLIMIT_AS, (memory_limit_bytes, memory_limit_bytes))
            print(f"Memory limit set to {args.memory_limit} GB")
            
            # Also try to limit torch memory usage if possible
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.set_per_process_memory_fraction(min(0.7, args.memory_limit / 32.0))
                    print("CUDA memory usage limited")
            except Exception as e:
                print(f"Note: Could not limit CUDA memory: {e}")
        except Exception as e:
            print(f"Failed to set memory limit: {e}")
    
    print(f"Using model: {args.model}")
    print("Memory optimization: Enabled")
    
    # Initialize indexer
    indexer = DocumentIndexer(
        es_host=args.es_host,
        index_name=args.index_name,
        model_name=args.model,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    
    # Index directory
    start_time = time.time()
    count = indexer.index_directory(args.directory, recursive=not args.no_recursive)
    elapsed_time = time.time() - start_time
    
    print(f"Indexed {count} document chunks in {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()
