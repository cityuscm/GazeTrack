import time
from typing import Callable

from attrs import frozen


@frozen
class Timestamped[T]:
    value: T
    timestamp: float = time.time()

    def map[U](self, f: Callable[[T], U]) -> "Timestamped[U]":
        return Timestamped(f(self.value), self.timestamp)

    def unwrap(self) -> T:
        return self.value
