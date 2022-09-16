import json
import uuid
from typing import Dict, List

from fastapi import (
    WebSocket,
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[uuid.UUID, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, id: uuid.UUID):
        print("Connecting", id)
        await websocket.accept()
        if id in self.active_connections and len(self.active_connections[id]) > 0:
            self.active_connections[id] = self.active_connections[id] + [websocket]
        else:
            self.active_connections[id] = [websocket]

    def disconnect(self, websocket: WebSocket, id: uuid.UUID):
        print("Disconnecting", id)
        if id in self.active_connections:
            self.active_connections[id] = [conn for conn in self.active_connections[id] if conn != websocket]

    async def send_to_id(self, id: uuid.UUID, data: dict):
        if id in self.active_connections:
            for connection in self.active_connections[id]:
                await connection.send_text(json.dumps(data))


socket_manager = ConnectionManager()
