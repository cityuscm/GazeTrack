import numpy as np
from aioreactive.subject import AsyncMultiSubject
from wireup import service

from DataContainer import GazeProjection, ClientInput, Matchable
from type import NDISourceStream


@service
def result_stream_factory() -> AsyncMultiSubject[tuple[int, GazeProjection]]:
    return AsyncMultiSubject[tuple[int, GazeProjection]]()


@service
def client_stream_factory() -> AsyncMultiSubject[ClientInput]:
    return AsyncMultiSubject()


@service
def scene_stream_factory() -> AsyncMultiSubject[np.ndarray]:
    return AsyncMultiSubject()


@service
def match_stream_factory() -> AsyncMultiSubject[Matchable]:
    return AsyncMultiSubject()

@service
def ndi_source_stream_factory() -> NDISourceStream:
    return NDISourceStream(AsyncMultiSubject())