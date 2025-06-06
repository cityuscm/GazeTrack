import asyncio
from typing import Iterable

from expression.system import AsyncDisposable


async def dispose_all(disposables: Iterable[AsyncDisposable]):
    for disposable in disposables:
        await disposable.dispose_async()

async def cancel_all(tasks: Iterable[asyncio.Task]):
    for task in tasks:
        task.cancel()