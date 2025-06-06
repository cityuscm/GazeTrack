import asyncio
import contextlib
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from wireup import Injected

from generator import client, scene
from services import NDIWatchdog
from services.ClientManager import WSClientManager
from type import ClientList
from uniques import matching_context

router = APIRouter()


class Session(BaseModel):
    clients: List[str]
    scene: str


@router.post("/session")
async def create_session(session: Session, clients: Injected[ClientList], ndi_watchdog: Injected[NDIWatchdog]):
    clients_ip: list[tuple[str, str]] = []
    for ip in session.clients:
        with contextlib.suppress(KeyError):
            clients_ip.append(clients[ip])
    world_source = ndi_watchdog.get(session.scene)
    connected = [client(info) for info in clients_ip]
    world_context = await scene(world_source)
    asyncio.create_task(matching_context(connected, world_context))
    return {"status": "ok"}


@router.get("/clients")
async def list_clients(clients: Injected[ClientList]):
    return list(clients.keys())


@router.get("/worlds")
async def list_worlds(ndi_watchdog: Injected[NDIWatchdog]):
    return ndi_watchdog.sources


@router.get("/info")
async def list_all(clients: Injected[ClientList], ndi_watchdog: Injected[NDIWatchdog]):
    return {
        "clients": list(clients.keys()),
        "worlds": list(ndi_watchdog.sources)
    }


@router.get("/auto")
async def auto_connect(clients: Injected[ClientList], ndi_watchdog: Injected[NDIWatchdog]):
    src = ndi_watchdog.sources[0]
    src = ndi_watchdog.get(src)
    src = await scene(src)
    conn = [client(it) for it in clients.values()]
    asyncio.create_task(matching_context(conn, src))
    return {"status": "ok"}


@router.websocket("/ws")
async def websocket_session(websocket: WebSocket, manager: Injected[WSClientManager]):
    manager.add(websocket)
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.remove(websocket)
