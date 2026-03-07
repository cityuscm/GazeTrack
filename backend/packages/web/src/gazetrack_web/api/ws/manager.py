import asyncio
import json
from typing import Any

from fastapi import WebSocket
from loguru import logger


class GazeWebSocketManager:
    def __init__(self):
        self._connections: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.append(websocket)
        logger.info(f"WS client connected. Total: {len(self._connections)}")

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections = [c for c in self._connections if c is not websocket]
        logger.info(f"WS client disconnected. Total: {len(self._connections)}")

    async def broadcast(self, data: Any) -> None:
        message = json.dumps(data)
        dead: list[WebSocket] = []
        for connection in list(self._connections):
            try:
                await connection.send_text(message)
            except Exception:
                dead.append(connection)
        if dead:
            async with self._lock:
                self._connections = [c for c in self._connections if c not in dead]
