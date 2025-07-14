#!/usr/bin/env python3
"""
WebSocket server for Doca
Provides API endpoints and WebSocket communication for the frontend
"""

import os
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import socketio
import uvicorn
from pathlib import Path

from src.core.indexer import DocumentIndexer
from src import config
from src.utils.es_health_check import wait_for_elasticsearch

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Doca API", description="API for Doca document indexer")

# Define allowed origins
allowed_origins = ["http://localhost:5173"]  # Add your frontend URL here

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create Socket.IO server with CORS handling disabled (let FastAPI handle it)
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])
socket_app = socketio.ASGIApp(sio)
# Mount at /socket.io (default path) instead of /ws
app.mount("/socket.io", socket_app)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Custom indexer class that reports progress via WebSocket
class WebSocketIndexer(DocumentIndexer):
    """Extended DocumentIndexer that reports progress via WebSocket"""
    
    async def index_directory_with_progress(self, directory_path: str, recursive: bool = True) -> int:
        """
        Index all supported files in a directory with progress reporting
        
        Args:
            directory_path: Path to the directory to index
            recursive: Whether to recursively search for files
            
        Returns:
            Number of chunks successfully indexed
        """
        indexed_count = 0
        
        try:
            # Get all supported files
            path = Path(directory_path)
            supported_extensions = list(self.parsers.keys())
            
            # Find all files with supported extensions
            all_files = []
            if recursive:
                for ext in supported_extensions:
                    all_files.extend(list(path.glob(f"**/*.{ext}")))
            else:
                for ext in supported_extensions:
                    all_files.extend(list(path.glob(f"*.{ext}")))
            
            # Sort files by size to process smaller files first
            all_files.sort(key=lambda p: p.stat().st_size)
            
            total_files = len(all_files)
            await sio.emit('indexing_started', {'total_files': total_files})
            
            # Index each file with progress updates
            for i, file_path in enumerate(all_files):
                try:
                    # Force garbage collection before processing each file
                    import gc
                    gc.collect()
                    
                    file_chunks = self.index_file(str(file_path))
                    indexed_count += file_chunks
                    
                    # Send progress update
                    progress = {
                        'current': i + 1,
                        'total': total_files,
                        'percentage': round((i + 1) / total_files * 100, 2),
                        'file_path': str(file_path),
                        'chunks_indexed': file_chunks
                    }
                    await sio.emit('indexing_progress', progress)
                    
                    # Small delay to prevent overwhelming the socket
                    await asyncio.sleep(0.05)  # Increased delay to give more time for memory cleanup
                except Exception as e:
                    error_msg = f"Error processing file {file_path}: {str(e)}"
                    print(error_msg)
                    await sio.emit('indexing_error', {
                        'file_path': str(file_path),
                        'error': error_msg
                    })
            
            # Send completion event
            await sio.emit('indexing_completed', {
                'total_files': total_files,
                'total_chunks': indexed_count
            })
            
            return indexed_count
        except Exception as e:
            error_msg = f"Error during indexing process: {str(e)}"
            print(error_msg)
            await sio.emit('indexing_error', {'error': error_msg})
            return indexed_count

# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def start_indexing(sid, data):
    """Start indexing process with the given parameters"""
    try:
        directory = data.get('directory', '')
        recursive = data.get('recursive', True)
        es_host = data.get('es_host', config.ES_HOST)
        index_name = data.get('index_name', config.INDEX_NAME)
        model_name = data.get('model_name', config.MODEL_NAME)
        chunk_size = data.get('chunk_size', config.CHUNK_SIZE)
        chunk_overlap = data.get('chunk_overlap', config.CHUNK_OVERLAP)
        recreate_index = data.get('recreate_index', True)  # По умолчанию пересоздаем индекс
        
        # Принудительно очищаем память перед началом индексации
        import gc
        gc.collect()
        
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
        
        # Отправляем сообщение о начале инициализации
        await sio.emit('indexing_status', {'status': 'initializing', 'message': 'Initializing indexer...'})
        
        # Check Elasticsearch connection first
        await sio.emit('indexing_status', {'status': 'checking', 'message': 'Checking Elasticsearch connection...'})
        
        if not wait_for_elasticsearch(es_host, max_retries=5, retry_interval=1):
            error_msg = f"Cannot connect to Elasticsearch at {es_host}. Please check if Elasticsearch is running."
            logger.error(error_msg)
            await sio.emit('indexing_error', {'error': error_msg})
            return {"status": "error", "message": error_msg}
        
        # Initialize indexer
        try:
            indexer = WebSocketIndexer(
                es_host=es_host,
                index_name=index_name,
                model_name=model_name,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                recreate_index=recreate_index,
            )
            
            # Start indexing in a background task
            await sio.emit('indexing_status', {'status': 'starting', 'message': 'Starting indexing process...'})
            asyncio.create_task(indexer.index_directory_with_progress(directory, recursive=recursive))
            
            return {"status": "started"}
        except ConnectionError as e:
            error_msg = f"Elasticsearch connection error: {str(e)}"
            logger.error(error_msg)
            await sio.emit('indexing_error', {'error': error_msg})
            return {"status": "error", "message": error_msg}
    except Exception as e:
        error_msg = f"Error starting indexing: {str(e)}"
        logger.error(error_msg)
        await sio.emit('indexing_error', {'error': error_msg})
        return {"status": "error", "message": error_msg}

# API routes
@app.get("/")
async def root():
    return {"message": "Welcome to Doca API"}

@app.get("/config")
async def get_config():
    """Get current configuration"""
    return {
        "es_host": config.ES_HOST,
        "index_name": config.INDEX_NAME,
        "model_name": config.MODEL_NAME,
        "chunk_size": config.CHUNK_SIZE,
        "chunk_overlap": config.CHUNK_OVERLAP,
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
