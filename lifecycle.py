import asyncio
from contextlib import asynccontextmanager

import wireup
from aioreactive import AsyncAnonymousObserver
from aioreactive.subject import AsyncMultiSubject
from expression.system import AsyncDisposable
from fastapi import FastAPI
from wireup import Injected

from DataContainer import GazeProjection
from background import device_discovery
from container import container
from listener import osc_broadcast, ws_feedback
from services.ClientManager import WSClientManager
from services.Watchdog import NDIWatchdog
from util.disposible import dispose_all, cancel_all


@asynccontextmanager
@wireup.inject_from_container(container=container)
async def lifespan(
        _: FastAPI,
        ndi_watchdog: Injected[NDIWatchdog],
        stream: Injected[AsyncMultiSubject[tuple[int, GazeProjection]]],
        ws_client_manager: Injected[WSClientManager]
):
    listeners: list[AsyncDisposable] = []
    tasks: list[asyncio.Task] = [asyncio.create_task(device_discovery())]
    listeners.append(await stream.subscribe_async(AsyncAnonymousObserver(osc_broadcast)))
    listeners.append(await stream.subscribe_async(AsyncAnonymousObserver(ws_feedback(ws_client_manager))))
    yield
    ndi_watchdog.stop()
    await dispose_all(listeners)
    await cancel_all(tasks)
