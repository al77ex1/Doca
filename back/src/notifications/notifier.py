"""
Base notifier interface for Doca backend
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class Notifier(ABC):
    """
    Abstract base class for notification systems
    """
    
    @abstractmethod
    async def send_status(self, status: str, message: str):
        """
        Send status update
        
        Args:
            status: Status code
            message: Status message
        """
        pass
    
    @abstractmethod
    async def send_progress(self, current: int, total: int, file_path: str, 
                           chunks_indexed: int, memory_usage_mb: Optional[float] = None):
        """
        Send progress update
        
        Args:
            current: Current progress
            total: Total items
            file_path: Current file path
            chunks_indexed: Number of chunks indexed
            memory_usage_mb: Optional memory usage in MB
        """
        pass
    
    @abstractmethod
    async def send_error(self, error: str, file_path: Optional[str] = None):
        """
        Send error notification
        
        Args:
            error: Error message
            file_path: Optional file path related to the error
        """
        pass
    
    @abstractmethod
    async def send_warning(self, warning: str, file_path: str):
        """
        Send warning notification
        
        Args:
            warning: Warning message
            file_path: File path related to the warning
        """
        pass
    
    @abstractmethod
    async def send_indexing_started(self, total_files: int, skipped_files: int):
        """
        Send indexing started notification
        
        Args:
            total_files: Total number of files to index
            skipped_files: Number of skipped files
        """
        pass
    
    @abstractmethod
    async def send_indexing_completed(self, total_files: int, total_chunks: int, 
                                     skipped_files: int, error_files: int):
        """
        Send indexing completed notification
        
        Args:
            total_files: Total number of files processed
            total_chunks: Total number of chunks indexed
            skipped_files: Number of skipped files
            error_files: Number of files with errors
        """
        pass
