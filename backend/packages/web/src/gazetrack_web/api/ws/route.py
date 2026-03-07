from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from gazetrack_web.api.ws.manager import GazeWebSocketManager


def ws_router(manager: GazeWebSocketManager) -> APIRouter:
    router = APIRouter()

    @router.websocket("/ws/gaze")
    async def gaze_ws(websocket: WebSocket):
        await manager.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            await manager.disconnect(websocket)

    return router
