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
    # Проверка на максимальный размер текста для предотвращения проблем с памятью
    max_safe_length = 10_000_000  # 10MB текста
    if len(text) > max_safe_length:
        print(f"Warning: Text is very large ({len(text)} chars). Truncating to {max_safe_length} chars.")
        text = text[:max_safe_length]
    
    chunks = []
    
    if len(text) <= chunk_size:
        chunks.append(text)
    else:
        start = 0
        while start < len(text):
            # Защита от бесконечного цикла
            if start >= len(text):
                break
                
            end = min(start + chunk_size, len(text))
            
            # Try to find a natural break point (period, newline, etc.)
            if end < len(text):
                found_break = False
                for break_char in ["\n\n", "\n", ". ", "! ", "? ", "; "]:
                    try:
                        natural_break = text.rfind(break_char, start, end)
                        if natural_break != -1 and natural_break > start + chunk_size // 2:
                            end = natural_break + len(break_char)
                            found_break = True
                            break
                    except Exception as e:
                        print(f"Error finding break point: {e}")
                        # Продолжаем с текущим end если возникла ошибка
                
                # Если не нашли подходящую точку разрыва, используем текущий end
                if not found_break:
                    # Убедимся, что end не превышает длину текста
                    end = min(end, len(text))
            
            # Защита от некорректных индексов
            if start >= end:
                break
                
            try:
                chunk = text[start:end]
                chunks.append(chunk)
            except Exception as e:
                print(f"Error creating chunk: {e}")
                break
                
            start = end - chunk_overlap
            
            # Защита от зацикливания
            if start == end:
                start += 1
    
    return chunks
