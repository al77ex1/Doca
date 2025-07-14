"""
Socket.IO event handlers for Doca backend
"""
import asyncio
import logging
import socketio
from typing import Dict, Any

from src import config
from src.notifications.socket_notifier import SocketNotifier
from src.services.indexing_service import IndexingService

# Configure logging
logger = logging.getLogger(__name__)

def register_socket_handlers(sio: socketio.AsyncServer):
    """
    Register Socket.IO event handlers
    
    Args:
        sio: Socket.IO server instance
    """
    
    @sio.event
    async def connect(sid, environ):
        """
        Handle client connection
        
        Args:
            sid: Session ID
            environ: WSGI environment
        """
        logger.info(f"Client connected: {sid}")

    @sio.event
    async def disconnect(sid):
        """
        Handle client disconnection
        
        Args:
            sid: Session ID
        """
        logger.info(f"Client disconnected: {sid}")

    @sio.event
    async def start_indexing(sid, data):
        """
        Start indexing process with the given parameters
        
        Args:
            sid: Session ID
            data: Indexing parameters
            
        Returns:
            dict: Status response
        """
        try:
            directory = data.get('directory', '')
            recursive = data.get('recursive', True)
            es_host = data.get('es_host', config.ES_HOST)
            index_name = data.get('index_name', config.INDEX_NAME)
            model_name = data.get('model_name', config.MODEL_NAME)
            chunk_size = data.get('chunk_size', config.CHUNK_SIZE)
            chunk_overlap = data.get('chunk_overlap', config.CHUNK_OVERLAP)
            recreate_index = data.get('recreate_index', True)
            
            # Create notifier
            notifier = SocketNotifier(sio)
            
            # Create indexing service
            indexing_service = IndexingService(
                notifier=notifier,
                es_host=es_host,
                index_name=index_name,
                model_name=model_name,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                recreate_index=recreate_index,
            )
            
            # Start indexing in a background task
            await notifier.send_status('starting', 'Starting indexing process...')
            asyncio.create_task(indexing_service.index_directory(directory, recursive=recursive))
            
            return {"status": "started"}
        except Exception as e:
            error_msg = f"Error starting indexing: {str(e)}"
            logger.error(error_msg)
            await sio.emit('indexing_error', {'error': error_msg})
            return {"status": "error", "message": error_msg}
