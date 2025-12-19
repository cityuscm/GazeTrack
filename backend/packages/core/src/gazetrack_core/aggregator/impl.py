import contextlib
from contextlib import asynccontextmanager
from typing import NamedTuple, AsyncGenerator, Self

import anyio
import asyncer
from anyio import AsyncContextManagerMixin, get_cancelled_exc_class
from cyndilib import Finder
from loguru import logger
from pupil_labs.realtime_api import discover_devices, Device

from gazetrack_core.aggregator.interface import Aggregator
from gazetrack_core.producer import (
    RTSPProducer,
    GazeProducer,
    NDIProducer,
)

url = NamedTuple("url", [("world", str), ("gaze", str)])


class RTSPAggregator(
    AsyncContextManagerMixin, Aggregator[tuple[RTSPProducer, GazeProducer]]
):
    def __init__(self):
        self._clients: dict[str, url] = {}
        self._client_addr: set[str] = set()
        pass

    @asynccontextmanager
    async def __asynccontextmanager__(self) -> AsyncGenerator[Self]:
        async with asyncer.create_task_group() as tg:
            tg.soonify(self._scan)()
            logger.info("RTSP Aggregator started")
            yield self
            tg.cancel_scope.cancel()
            logger.info("RTSP Aggregator stopped")

    async def _scan(self):
        with contextlib.suppress(get_cancelled_exc_class()):
            async for info in discover_devices():
                with anyio.move_on_after(5):
                    async with Device.from_discovered_device(info) as device:
                        address = device.address
                        logger.info(f"Detected {address}")
                        status = await device.get_status()
                        sensor_gaze = status.direct_gaze_sensor()
                        sensor_world = status.direct_world_sensor()
                        if sensor_gaze.connected and sensor_world.connected:
                            self._clients[address] = url(
                                sensor_world.url, sensor_gaze.url
                            )
                            self._client_addr.add(address)
                            logger.info(f"Discovered {address}")

    @property
    def sources(self):
        return self._clients

    def get(self, addr: str) -> tuple[RTSPProducer, GazeProducer]:
        if addr not in self._clients:
            raise ValueError("Client not found")
        x = self._clients[addr]
        return RTSPProducer(x.world), GazeProducer(x.gaze)


class NDIAggregator(AsyncContextManagerMixin, Aggregator[NDIProducer]):
    def __init__(self, interval: float = 1.0):
        self._finder: Finder | None = None
        self._src: list[str] = []
        self._interval = interval
        pass

    @asynccontextmanager
    async def __asynccontextmanager__(self) -> AsyncGenerator[Self]:
        async with asyncer.create_task_group() as tg:
            tg.soonify(self._scan)()
            logger.info("NDI Aggregator started")
            yield self
            tg.cancel_scope.cancel()
            logger.info("NDI Aggregator stopped")

    async def _scan(self):
        with contextlib.suppress(get_cancelled_exc_class()), Finder() as self._finder:
            while True:
                with anyio.move_on_after(self._interval):
                    self._finder.update_sources()
                    self._src = self._finder.get_source_names()
                    await anyio.sleep(0)
        self._finder = None
        self._src = []

    @property
    def sources(self) -> list[str]:
        return self._src

    def get(self, src: str) -> NDIProducer:
        if self._finder:
            return NDIProducer(self._finder.get_source(src))
        raise ValueError("Finder is not running")
