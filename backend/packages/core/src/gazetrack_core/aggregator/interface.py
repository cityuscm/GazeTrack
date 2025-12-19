from typing import Protocol


class Aggregator[T](Protocol):
    @property
    def sources(self) -> list[str]: ...

    def get(self, src: str) -> T: ...
