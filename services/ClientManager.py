from starlette.websockets import WebSocket
from wireup import service


@service
class WSClientManager:
    def __init__(self):
        self.connections: list[WebSocket] = []

    def add(self, ws: WebSocket):
        self.connections.append(ws)

    def remove(self, ws: WebSocket):
        self.connections.remove(ws)

    async def broadcast(self, message: str):
        for ws in self.connections:
            await ws.send_text(message)

    async def broadcast_json(self, message: dict):
        for ws in self.connections:
            await ws.send_json(message)