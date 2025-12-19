from contextlib import asynccontextmanager, AsyncExitStack
from typing import Callable, AsyncGenerator, Self

import anyio
import asyncer
import numpy as np
from anyio import AsyncContextManagerMixin
from loguru import logger

from gazetrack_core.event.EventBus import EventBus, Event
from gazetrack_core.function.functions import assemble_payload, stamp
from gazetrack_core.pipeline.interfaces import Pipeline
from gazetrack_core.producer.interface import Producer


class Engine(AsyncContextManagerMixin):
    def __init__(
        self,
        fn: Pipeline,
        bus: EventBus,
        source_producers: list[Producer[np.ndarray]] = None,
        gaze_producers: list[Producer[tuple[float, float]]] = None,
        scene_producer: Producer[np.ndarray] = None,
    ):
        self._pp = source_producers
        self._gp = gaze_producers
        self._sp = scene_producer

        self._fn = fn
        self._bus = bus

        self._lock = anyio.Lock()

        self.context = asyncer.create_task_group()

    @asynccontextmanager
    async def __asynccontextmanager__(self) -> AsyncGenerator[Self]:
        async with self.context:
            yield self

    @staticmethod
    def safe(method: Callable):
        async def wrapper(self, *args, **kwargs):
            is_running = self.running
            if is_running:
                self.halt()
            async with self._lock:
                await method(self, *args, **kwargs)
            if is_running:
                self()

        return wrapper

    @property
    def assembled(self) -> bool:
        return self._pp is not None and self._gp is not None and self._sp is not None

    @property
    def running(self) -> bool:
        return self._lock.locked()

    @safe
    async def set_source_producers(self, source_producers: list[Producer[np.ndarray]]):
        self._pp = source_producers

    @safe
    async def set_gaze_producers(
        self, gaze_producers: list[Producer[tuple[float, float]]]
    ):
        self._gp = gaze_producers

    @safe
    async def set_scene_producer(self, scene_producer: Producer[np.ndarray]):
        self._sp = scene_producer

    @safe
    async def set_environment(
        self,
        source_producers: list[Producer[np.ndarray]],
        gaze_producers: list[Producer[tuple[float, float]]],
        scene_producer: Producer[np.ndarray],
    ):
        self._pp = source_producers
        self._gp = gaze_producers
        self._sp = scene_producer

    @safe
    async def set_pipeline(self, fn: Pipeline):
        self._fn = fn

    async def _ctx(self, stack: AsyncExitStack):
        for client in self._pp:
            await stack.enter_async_context(client)
            logger.info(f"{client} initialized")
        for client in self._gp:
            await stack.enter_async_context(client)
            logger.info(f"{client} initialized")
        await stack.enter_async_context(self._sp)
        logger.info(f"{self._sp} initialized")

    async def _pass(self) -> None:
        try:
            it = assemble_payload(self._pp, self._gp, self._sp)
            it = stamp(it)
            result = await asyncer.asyncify(self._fn)(it)
            await self._bus.publish(Event("result", result))
        except RuntimeError as e:
            await self._bus.publish(Event("error", str(e)))
        await anyio.sleep(0)

    async def _loop(self) -> None:
        async with self._lock:
            async with AsyncExitStack() as stack:
                await self._ctx(stack)
                logger.info("Engine started")
                while True:
                    await self._pass()

    def halt(self):
        self.context.cancel_scope.cancel()

    def __call__(self, *args, **kwargs) -> bool:
        if self.running or not self.assembled:
            return False
        self.context.soonify(self._loop)()
        return True
