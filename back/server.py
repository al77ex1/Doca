#!/usr/bin/env python3
"""
WebSocket server for Doca
Provides API endpoints and WebSocket communication for the frontend
"""

import logging
import uvicorn
from fastapi import FastAPI, WebSocket

from src.app.factory import create_app
from src.api.routes import router
from src.api.websocket import websocket_endpoint
from src.api.socket_handlers import register_socket_handlers
from src.utils.es_health_check import wait_for_elasticsearch

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastAPI app and Socket.IO server
app, sio = create_app()

# Register API routes
app.include_router(router)

# Register WebSocket endpoint
app.add_api_websocket_route("/ws", websocket_endpoint)

# Register Socket.IO event handlers
register_socket_handlers(sio)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
