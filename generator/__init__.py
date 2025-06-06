import asyncio
from fractions import Fraction
from typing import Optional

import cv2
import numpy as np
from cyndilib import VideoFrameSync, Receiver, Source, RecvBandwidth, RecvColorFormat
from pupil_labs.realtime_api import receive_video_frames, receive_gaze_data

from interfaces import StopperGetter


def client(info: tuple[str, str]) -> StopperGetter[tuple[np.ndarray, tuple[float, float]]]:
    frame: Optional[np.ndarray] = None
    gaze: tuple[float, float] = (0, 0)

    async def fetch_frame():
        nonlocal frame
        async for frame in receive_video_frames(info[0]):
            frame = frame.bgr_buffer()
            await asyncio.sleep(0)

    async def fetch_gaze():
        nonlocal gaze
        async for gaze in receive_gaze_data(info[1]):
            gaze = (gaze.x, gaze.y)
            await asyncio.sleep(0)

    t1 = asyncio.create_task(fetch_frame())
    t2 = asyncio.create_task(fetch_gaze())

    def stop() -> None:
        nonlocal t1, t2
        t1.cancel()
        t2.cancel()

    def get() -> tuple[np.ndarray, tuple[float, float]]:
        nonlocal frame, gaze
        return frame, gaze

    return StopperGetter(stop=stop, get=get)


async def scene(source: Source) -> StopperGetter[np.ndarray]:
    frame: Optional[np.ndarray]
    resolution: Optional[tuple[int, int]]
    frame_rate: Optional[Fraction]
    receiver = Receiver(
        color_format=RecvColorFormat.BGRX_BGRA,
        bandwidth=RecvBandwidth.highest
    )
    receiver.set_source(source)
    frame_sync = VideoFrameSync()
    receiver.set_source(source)
    receiver.frame_sync.set_video_frame(frame_sync)

    attempts = 0
    while not receiver.is_connected():
        attempts += 1
        await asyncio.sleep(0.1 + attempts * 0.1)
        if attempts > 10:
            raise Exception("Failed to connect to NDI source")

    while True:
        receiver.frame_sync.capture_video()
        resolution = frame_sync.get_resolution()
        if min(resolution) > 0 and frame_sync.get_data_size() > 0:
            frame_rate = frame_sync.get_frame_rate()
            break
        await asyncio.sleep(0.1)

    async def fetch():
        nonlocal frame
        try:
            while True:
                receiver.frame_sync.capture_video()
                frame = frame_sync.get_array().reshape(resolution[1], resolution[0], 4)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                await asyncio.sleep(1 / float(frame_rate))
        except asyncio.CancelledError:
            pass
        finally:
            receiver.disconnect()

    t = asyncio.create_task(fetch())

    def stop() -> None:
        nonlocal t
        t.cancel()

    def get() -> np.ndarray:
        nonlocal frame
        return frame

    return StopperGetter(stop=stop, get=get)
