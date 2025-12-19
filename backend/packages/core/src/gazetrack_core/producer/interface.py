from typing import Protocol


class Producer[T](Protocol):
    def produce(self) -> T: ...
