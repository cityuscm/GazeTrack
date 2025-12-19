from typing import List, Callable

from fastapi import APIRouter

from gazetrack_web.api.model import Session
from gazetrack_core.event.EventBus import EventBus, Event


def default_router(
    get_clients: Callable[[], List[str]],
    get_scenes: Callable[[], List[str]],
    get_running: Callable[[], bool],
    bus: EventBus,
):
    router = APIRouter(prefix="/api")

    @router.get("/clients")
    async def clients():
        return get_clients()

    @router.get("/scenes")
    async def scenes():
        return get_scenes()

    @router.get("/status")
    async def running():
        return get_running()

    @router.post("/session")
    async def set_session(session: Session):
        await bus.publish(Event("set_session", session))
        return {"session": session}

    @router.post("/control")
    async def control(start: bool):
        await bus.publish(Event("control", start))
        return {"start": start}

    return router
