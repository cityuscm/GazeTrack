from dataclasses import dataclass

import numpy as np

from DataContainer.vector import Vec2i, Vec2


@dataclass(frozen=True, slots=True)
class GazeProjection:
    bounding_box: Vec2i
    coordinates: Vec2

    @property
    def center_offset(self) -> Vec2:
        w, h = self.bounding_box
        x, y = self.coordinates
        center_x = w / 2
        center_y = h / 2
        offset_x = (x - center_x) / w
        offset_y = (y - center_y) / h
        return Vec2(offset_x, -offset_y)

    @property
    def normalized_coordinates(self) -> Vec2:
        w, h = self.bounding_box
        x, y = self.coordinates
        return Vec2(x / w, y / h)

@dataclass
class ImageDimensions:
    width: int
    height: int
    ratio = property(lambda self: self.width / self.height)
    center = property(lambda self: np.array([self.width / 2, self.height / 2]))
    bounding_box = property(lambda self: np.array([[0, 0], [self.width, self.height]]))
    corners = property(
        lambda self: np.float32(
            [
                np.array([0, 0]),
                np.array([self.width, 0]),
                np.array([self.width, self.height]),
                np.array([0, self.height]),
            ]
        )
    )

@dataclass(frozen=True)
class Matchable:
    view: np.ndarray
    gaze: tuple[float, float]
    scene: np.ndarray
    id: int


@dataclass(frozen=True)
class ClientInput:
    id: int
    view: np.ndarray
    gaze: tuple[float, float]
