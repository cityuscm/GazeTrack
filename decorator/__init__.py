import asyncio
import contextlib
from functools import wraps
from typing import Callable, Optional, Any, Coroutine


def unique[T](func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
    current_task: Optional[asyncio.Task] = None

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        nonlocal current_task

        # Cancel previous task if it exists and is running
        if current_task and not current_task.done():
            current_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await current_task

        # Create and store new task
        current_task = asyncio.create_task(func(*args, **kwargs))
        try:
            return await current_task
        except asyncio.CancelledError:
            # If the task is cancelled from outside, clean up
            current_task = None
            raise

    return wrapper
