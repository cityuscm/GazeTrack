import contextlib
from contextlib import asynccontextmanager
from fractions import Fraction
from typing import AsyncGenerator, Self

import anyio
import asyncer
import numpy as np
from anyio import AsyncContextManagerMixin
from cyndilib import Receiver, VideoFrameSync, Source, RecvColorFormat, RecvBandwidth
from pupil_labs.realtime_api import receive_video_frames, receive_gaze_data
from tenacity import RetryError, AsyncRetrying, stop_after_attempt, wait_exponential

from gazetrack_core.producer.interface import Producer
from gazetrack_core.struct import Timestamped, Payload
from gazetrack_core.utils import unzip2


class PayloadProducer(Producer[Timestamped[Payload]]):
    def __init__(
        self,
        scene_producer: Producer[np.ndarray],
        client_producer: list[
            tuple[Producer[np.ndarray], Producer[tuple[float, float]]]
        ],
    ):
        self._pov_producer, self._gaze_producer = unzip2(client_producer)
        self._scene_producer = scene_producer

    def produce(self) -> Timestamped[Payload]:
        return Timestamped(
            Payload(
                visual=[p.produce() for p in self._pov_producer],
                gaze=[p.produce() for p in self._gaze_producer],
                scene=self._scene_producer.produce(),
            )
        )


class RTSPProducer(AsyncContextManagerMixin, Producer[np.ndarray]):
    @asynccontextmanager
    async def __asynccontextmanager__(self):
        async with asyncer.create_task_group() as tg:
            tg.soonify(self.coroutine)()
            await self._ready.wait()
            yield self
            tg.cancel_scope.cancel()

    def __init__(self, url: str):
        super().__init__()
        self._url = url
        self._ready = anyio.Event()
        self._frame: np.ndarray | None = None

    async def coroutine(self):
        async for frame in receive_video_frames(self._url):
            self._frame = frame.bgr_buffer()
            self._ready.set()
            await anyio.sleep(0)

    def produce(self) -> np.ndarray:
        return self._frame


class GazeProducer(AsyncContextManagerMixin, Producer[tuple[float, float]]):
    @asynccontextmanager
    async def __asynccontextmanager__(self):
        async with asyncer.create_task_group() as tg:
            tg.soonify(self.coroutine)()
            yield self
            tg.cancel_scope.cancel()

    def __init__(self, url: str):
        super().__init__()
        self._url = url
        self._gaze: tuple[float, float] = (0, 0)

    async def coroutine(self):
        async for gaze in receive_gaze_data(self._url):
            self._gaze = (gaze.x, gaze.y)
            await anyio.sleep(0)

    def produce(self) -> tuple[float, float]:
        return self._gaze


class NDIProducer(AsyncContextManagerMixin, Producer[np.ndarray]):
    _receiver: Receiver
    _frameSync: VideoFrameSync
    _frame: np.ndarray
    _frame_rate: Fraction

    def __init__(self, src: Source):
        self._src = src
        self._ready = anyio.Event()

    @property
    def _retry_strategy(self):
        return AsyncRetrying(
            stop=stop_after_attempt(10),
            wait=wait_exponential(multiplier=0.1, min=0.1, max=1),
            sleep=anyio.sleep,
        )

    @asynccontextmanager
    async def __asynccontextmanager__(self) -> AsyncGenerator[Self]:
        self._receiver = Receiver(
            color_format=RecvColorFormat.BGRX_BGRA, bandwidth=RecvBandwidth.highest
        )
        self._receiver.set_source(self._src)
        self._frameSync = VideoFrameSync()
        self._receiver.frame_sync.set_video_frame(self._frameSync)
        initialized = await self._init(await self._conn())
        if not initialized:
            raise Exception("Failed to initialize NDI producer")
        async with asyncer.create_task_group() as tg:
            tg.soonify(self._fetch)()
            yield self
            tg.cancel_scope.cancel()

    def _capture(self):
        self._frame = self._frameSync.get_array().reshape(
            self._frameSync.get_resolution()[1], self._frameSync.get_resolution()[0], 4
        )[:, :, :3]

    async def _conn(self) -> bool:
        with contextlib.suppress(RetryError):
            async for attempts in self._retry_strategy:
                with attempts:
                    if self._receiver.is_connected():
                        return True
                    raise Exception("Failed to connect to NDI source")
        return False

    async def _init(self, connected: bool) -> bool:
        if not connected:
            return False
        with contextlib.suppress(RetryError):
            async for attempts in self._retry_strategy:
                with attempts:
                    self._receiver.frame_sync.capture_video()
                    resolution = self._frameSync.get_resolution()
                    if min(resolution) > 0 and self._frameSync.get_data_size() > 0:
                        self._frame_rate = self._frameSync.get_frame_rate()
                        self._capture()
                        return True
                    raise Exception("Failed to initialize NDI producer")
        return False

    async def _fetch(self) -> None:
        with contextlib.suppress(anyio.get_cancelled_exc_class()):
            while True:
                self._receiver.frame_sync.capture_video()
                self._capture()
                self._ready.set()
                await anyio.sleep_until(
                    anyio.current_time() + (1.0 / float(self._frame_rate))
                )

    def produce(self) -> np.ndarray:
        return self._frame
