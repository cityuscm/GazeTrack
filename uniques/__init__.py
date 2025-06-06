import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

import numpy as np
import wireup
from aioreactive.subject import AsyncMultiSubject
from wireup import Injected

from DataContainer import GazeProjection
from decorator import unique
from interfaces import StopperGetter
from container import container


@unique
@wireup.inject_from_container(container=container)
async def matching_context(
        client_sources: list[StopperGetter[tuple[np.ndarray, tuple[float, float]]]],
        world_source: StopperGetter[np.ndarray],
        stream: Injected[AsyncMultiSubject[tuple[int, GazeProjection]]],
        executor: Injected[ThreadPoolExecutor],
        match: Injected[Callable[[tuple[tuple[np.ndarray, tuple[float, float]], np.ndarray]], GazeProjection | None]]
):
    loop = asyncio.get_running_loop()
    i = 0
    try:
        while True:
            client_source = client_sources[i]
            world_frame = world_source.get()
            client_frame, client_gaze = client_source.get()
            if client_frame is None or world_frame is None or client_gaze is None:
                await asyncio.sleep(0)
                continue
            try:
                future = loop.run_in_executor(executor, match, ((client_frame, client_gaze), world_frame))
                result = await future
            except Exception:
                await asyncio.sleep(0)
                continue
            if result is not None:
                i = (i + 1) % len(client_sources)  # round-robin
                await stream.asend((i, result))
    except asyncio.CancelledError:
        world_source.stop()
        for client_source in client_sources:
            client_source.stop()
