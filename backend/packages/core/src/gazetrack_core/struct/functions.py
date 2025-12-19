import numpy as np
from returns.result import Result, Failure, Success

from gazetrack_core.struct import Projection


def out_of_bound(projection: Projection) -> bool:
    return (
        projection.gaze[0] < 0
        or projection.gaze[0] > projection.bound[0]
        or projection.gaze[1] < 0
        or projection.gaze[1] > projection.bound[1]
    )


def center_offset(projection: Projection) -> tuple[float, float]:
    width, height = projection.bound
    x, y = projection.gaze
    rx = np.interp(x, [0, width], [-0.5, 0.5])
    ry = np.interp(y, [0, height], [0.5, -0.5])
    return rx, ry


def center_offset_safe(projection: Projection) -> Result[tuple[float, float], None]:
    if out_of_bound(projection):
        return Failure(None)
    return Success(center_offset(projection))


def absolute_safe(projection: Projection) -> Result[tuple[float, float], None]:
    if out_of_bound(projection):
        return Failure(None)
    return Success(projection.gaze)


def normalized(projection: Projection) -> tuple[float, float]:
    width, height = projection.bound
    x, y = projection.gaze
    return (x / width), (y / height)
