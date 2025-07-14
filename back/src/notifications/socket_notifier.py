"""
Socket.IO notifier implementation for Doca backend
"""
from typing import Dict, Any, Optional
import socketio
from .notifier import Notifier

class SocketNotifier(Notifier):
    """
    Socket.IO implementation of the Notifier interface
    """
    
    def __init__(self, sio: socketio.AsyncServer):
        """
        Initialize Socket.IO notifier
        
        Args:
            sio: Socket.IO server instance
        """
        self.sio = sio
    
    async def send_status(self, status: str, message: str):
        """
        Send status update via Socket.IO
        
        Args:
            status: Status code
            message: Status message
        """
        await self.sio.emit('indexing_status', {'status': status, 'message': message})
    
    async def send_progress(self, current: int, total: int, file_path: str, 
                           chunks_indexed: int, memory_usage_mb: Optional[float] = None):
        """
        Send progress update via Socket.IO
        
        Args:
            current: Current progress
            total: Total items
            file_path: Current file path
            chunks_indexed: Number of chunks indexed
            memory_usage_mb: Optional memory usage in MB
        """
        progress = {
            'current': current,
            'total': total,
            'percentage': round(current / total * 100, 2),
            'file_path': str(file_path),
            'chunks_indexed': chunks_indexed
        }
        
        if memory_usage_mb is not None:
            progress['memory_usage_mb'] = round(memory_usage_mb, 2)
            
        await self.sio.emit('indexing_progress', progress)
    
    async def send_error(self, error: str, file_path: Optional[str] = None):
        """
        Send error notification via Socket.IO
        
        Args:
            error: Error message
            file_path: Optional file path related to the error
        """
        data = {'error': error}
        if file_path:
            data['file_path'] = str(file_path)
        await self.sio.emit('indexing_error', data)
    
    async def send_warning(self, warning: str, file_path: str):
        """
        Send warning notification via Socket.IO
        
        Args:
            warning: Warning message
            file_path: File path related to the warning
        """
        await self.sio.emit('indexing_warning', {
            'file_path': str(file_path),
            'warning': warning
        })
    
    async def send_indexing_started(self, total_files: int, skipped_files: int):
        """
        Send indexing started notification via Socket.IO
        
        Args:
            total_files: Total number of files to index
            skipped_files: Number of skipped files
        """
        await self.sio.emit('indexing_started', {
            'total_files': total_files,
            'skipped_files': skipped_files
        })
    
    async def send_indexing_completed(self, total_files: int, total_chunks: int, 
                                     skipped_files: int, error_files: int):
        """
        Send indexing completed notification via Socket.IO
        
        Args:
            total_files: Total number of files processed
            total_chunks: Total number of chunks indexed
            skipped_files: Number of skipped files
            error_files: Number of files with errors
        """
        await self.sio.emit('indexing_completed', {
            'total_files': total_files,
            'total_chunks': total_chunks,
            'skipped_files': skipped_files,
            'error_files': error_files
        })
