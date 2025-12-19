from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import ormsgpack
from websockets import serve, ServerConnection

from gazetrack_core.event.EventBus import AbstractEventBus


@asynccontextmanager
async def ws_remote_event_listener(bus: AbstractEventBus) -> AsyncGenerator[None, None]:
    def unpack(message: bytes) -> dict[str, Any] | None:
        try:
            data: dict[str, Any] = ormsgpack.unpackb(message)
            if data is not dict:
                raise TypeError
        except (ValueError, TypeError):
            return None
        return data

    async def fn(ws: ServerConnection):
        async for message in ws:
            match message:
                case bytes(message):
                    data = unpack(message)
                    if data is None:
                        continue
                    if "topic" in data and "payload" in data:
                        topic = data["topic"]
                        payload = data["payload"]
                        await bus.emit(topic, payload)
                case str(_):
                    continue

    async with serve(fn, "0.0.0.0", 8765) as server:
        await server.start_serving()
        yield
        server.close()
        await server.wait_closed()
