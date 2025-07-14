"""
Application factory for Doca backend
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    """
    Create and configure FastAPI application with Socket.IO
    
    Returns:
        tuple: (FastAPI app, Socket.IO server)
    """
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
    
    return app, sio
