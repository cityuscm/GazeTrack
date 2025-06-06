from dataclasses import dataclass


@dataclass
class State[T]:
    value: T