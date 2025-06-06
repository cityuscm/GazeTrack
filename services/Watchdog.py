import asyncio

from cyndilib import Finder, Source
from wireup import service, Injected


@service
class NDIWatchdog:
    def __init__(self, finder: Injected[Finder]):
        self._finder = finder
        self._sources: list[str] = []
        self._discovery_task = asyncio.create_task(self.run_discovery())

    async def run_discovery(self):
        try:
            while True:
                self._finder.update_sources()
                current_sources = self._finder.get_source_names()
                if current_sources != self._sources:
                    self._sources = current_sources
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    @property
    def sources(self):
        return self._finder.get_source_names()

    def get(self, name: str) -> Source:
        return self._finder.get_source(name)

    def stop(self):
        self._discovery_task.cancel()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.stop()
