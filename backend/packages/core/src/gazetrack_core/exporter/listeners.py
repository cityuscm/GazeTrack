from gazetrack_core.event.EventBus import EventBus
from gazetrack_core.exporter import Exporter


async def exporter_listener_from[T](bus: EventBus, exporter: Exporter[T]) -> None:
    async with bus.subscribe("result") as stream:
        async for event in stream:
            exporter(event.payload)
