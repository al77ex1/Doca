"""
Text chunking utilities for Doca
Provides functions for splitting text into chunks with overlap
"""

from typing import List


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """
    Split text into chunks with overlap
    
    Args:
        text: Text to split into chunks
        chunk_size: Maximum size of each chunk in characters
        chunk_overlap: Overlap between chunks in characters
        
    Returns:
        List of text chunks
    """
    # Strict limit on text size to prevent memory issues
    max_safe_length = 500_000  # 500KB text maximum (reduced from 10MB)
    if len(text) > max_safe_length:
        print(f"Warning: Text is very large ({len(text)} chars). Truncating to {max_safe_length} chars.")
        text = text[:max_safe_length]
    
    # Enforce reasonable chunk size limits
    if chunk_size > 1000:
        print(f"Warning: Chunk size {chunk_size} is too large. Limiting to 1000 characters.")
        chunk_size = 1000
        
    if chunk_overlap > chunk_size // 2:
        print(f"Warning: Chunk overlap {chunk_overlap} is too large. Limiting to {chunk_size // 2} characters.")
        chunk_overlap = chunk_size // 2
    
    # Initialize result list with a reasonable capacity estimate
    estimated_chunks = max(1, len(text) // (chunk_size - chunk_overlap) + 1)
    
    # Используем значение из конфигурации вместо жестко закодированного
    from src import config
    max_chunks = config.MAX_CHUNKS_PER_FILE  # Берем лимит из конфигурации
    
    # Выводим информацию о потенциальном количестве чанков до ограничения
    print(f"Estimated chunks before any limits: {estimated_chunks}")
    
    chunks = []
    
    if len(text) <= chunk_size:
        chunks.append(text)
    else:
        start = 0
        chunk_count = 0
        
        while start < len(text) and chunk_count < max_chunks:
            # Safety check
            if start >= len(text):
                break
                
            end = min(start + chunk_size, len(text))
            
            # Try to find a natural break point (period, newline, etc.)
            if end < len(text):
                found_break = False
                # Prioritize paragraph breaks first, then sentences, then other punctuation
                for break_char in ["\n\n", "\n", ". ", "! ", "? ", "; ", ", "]:
                    try:
                        # Look for break points in the second half of the chunk for better distribution
                        min_break_point = start + (chunk_size // 3)
                        natural_break = text.rfind(break_char, min_break_point, end)
                        if natural_break != -1:
                            end = natural_break + len(break_char)
                            found_break = True
                            break
                    except Exception as e:
                        print(f"Error finding break point: {e}")
                        # Continue with current end if there was an error
                
                # If no suitable break point was found, use the current end
                if not found_break:
                    end = min(end, len(text))
            
            # Safety check for invalid indices
            if start >= end or start >= len(text) or end > len(text):
                break
                
            try:
                chunk = text[start:end]
                if chunk.strip():  # Only add non-empty chunks
                    chunks.append(chunk)
                    chunk_count += 1
                    # Добавляем отладочную информацию для первых 5 чанков и каждого 10-го
                    if chunk_count <= 5 or chunk_count % 10 == 0:
                        # Первые 20 символов чанка
                        preview = chunk[:20].replace('\n', ' ').strip()
            except Exception as e:
                print(f"Error creating chunk: {e}")
                break
                
            # Move to next chunk position
            old_start = start
            start = end - chunk_overlap
            
            # Проверка на повторяющиеся чанки
            if len(chunks) >= 2 and chunk == chunks[-2]:
                print(f"Warning: Detected duplicate chunk at position {chunk_count}. Skipping overlap.")
                start = end  # Пропускаем перекрытие для этого чанка
            
            # Проверка на маленький прогресс или отсутствие прогресса
            if start <= old_start or (end - start < 10 and chunk_count > 5):
                print(f"Warning: Small or no progress in chunking: moved only {start - old_start} characters forward")
                # Увеличиваем прогресс, чтобы избежать создания слишком многих похожих чанков
                start = end  # Пропускаем перекрытие для этого чанка
            
            # Prevent infinite loops
            if start == end:
                start += 1
                
            # Check if we've reached the maximum number of chunks
            if chunk_count >= max_chunks:
                print(f"Warning: Maximum number of chunks ({max_chunks}) reached. Some text may not be processed.")
                break
    
    # Выводим фактическое количество созданных чанков
    print(f"Actual chunks created: {len(chunks)}")
    
    return chunks
