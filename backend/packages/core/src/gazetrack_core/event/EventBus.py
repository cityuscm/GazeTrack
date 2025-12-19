from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Protocol

import aioreactive as rx
from aioreactive import AsyncIteratorObserver
from aioreactive import AsyncObservable, AsyncSubject


@dataclass
class Event:
    topic: str
    payload: Any


class AbstractEventBus(Protocol):
    def subscribe(self, topic: str) -> AsyncObservable[Event]: ...
    def publish(self, event: Event) -> None: ...


class EventBus(AbstractEventBus):
    def __init__(self):
        self._sub: dict[str, AsyncSubject] = {}

    @asynccontextmanager
    async def subscribe(
        self, topic: str
    ) -> AsyncGenerator[AsyncIteratorObserver[Event], None]:
        observable = self._sub.setdefault(topic, AsyncSubject())
        filtered: AsyncObservable[Event] = rx.pipe(
            observable,
            rx.filter(lambda x: x.topic == topic),
            rx.map(lambda x: Event(topic, x.payload)),
        )
        observer = AsyncIteratorObserver(filtered)
        async with await filtered.subscribe_async(observer) as sub:
            try:
                yield observer
            finally:
                await sub.dispose_async()

    async def publish(self, event: Event) -> None:
        if event.topic in self._sub:
            await self._sub[event.topic].asend(event)
