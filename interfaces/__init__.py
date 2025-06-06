from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class StopperGetter[T]:
    stop: Callable[[], None]
    get: Callable[[], T]
