from typing import Protocol


class Exporter[T](Protocol):
    def __call__(self, value: T) -> None: ...
