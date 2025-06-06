from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class Vec2i:
    x: int
    y: int

    @property
    def numpy(self) -> np.ndarray:
        return np.int32([self.y, self.x])

    @classmethod
    def from_cv(cls, arr: np.ndarray):
        return cls(int(arr[1]), int(arr[0]))

    def __iter__(self):
        return iter([self.x, self.y])


@dataclass(frozen=True, slots=True)
class Vec2:
    x: float
    y: float

    @property
    def numpy(self) -> np.ndarray:
        return np.float32([self.y, self.x])

    @classmethod
    def from_cv(cls, arr: np.ndarray):
        return cls(int(arr[1]), int(arr[0]))

    def __iter__(self):
        return iter([self.x, self.y])