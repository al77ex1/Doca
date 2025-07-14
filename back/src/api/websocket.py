"""
WebSocket connection management for Doca backend
"""
from typing import List
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    """
    Manager for WebSocket connections
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Connect a new WebSocket client
        
        Args:
            websocket: WebSocket connection to add
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """
        Disconnect a WebSocket client
        
        Args:
            websocket: WebSocket connection to remove
        """
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        """
        Broadcast a message to all connected clients
        
        Args:
            message: Message to broadcast
        """
        for connection in self.active_connections:
            await connection.send_text(message)

# Create a singleton instance
manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint handler
    
    Args:
        websocket: WebSocket connection
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
