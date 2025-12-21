---
title: Engine
description: Async orchestration entrypoint for matcher pipelines and producers.
sidebar:
  badge: { text: "Module", variant: "success" }
---

# Classes

## `Engine` :badge[Class]{variant=note}
- **Module:** `packages.core.src.matcher_core.engine.Engine`
- **Signature:** `class Engine(AsyncContextManagerMixin)`
- **Purpose:** Coordinates producers, the pipeline, and the event bus in an async processing loop.
@backend/packages/core/src/matcher_core/engine/Engine.py#1-15

### Constructor :badge[Method]{variant=tip}
```python
Engine(
  fn: Pipeline,
  bus: EventBus,
  source_producers: list[Producer[np.ndarray]] | None = None,
  gaze_producers: list[Producer[tuple[float, float]]] | None = None,
  scene_producer: Producer[np.ndarray] | None = None,
)
```
- Binds the pipeline, event bus, and optional producer collections.
- Initializes a shared `anyio.Lock` and async task group used to run the processing loop.
@backend/packages/core/src/matcher_core/engine/Engine.py#16-35

### Context manager :badge[Method]{variant=tip} :badge[Async]{variant=caution}
```python
async def __asynccontextmanager__(self) -> AsyncGenerator[Engine, None]
```
- Delegates lifecycle management to the internal task group so you can `async with Engine(...)` in application code.
@backend/packages/core/src/matcher_core/engine/Engine.py#36-40

### `safe` :badge[Static]{variant=caution}
```python
@staticmethod
def safe(method: Callable) -> Callable
```
- Decorator that halts the engine when mutating configuration, acquires the lock, executes the method, and restarts if it was previously running.
- Applied to all mutator methods to guarantee consistent state when producer lists change.
@backend/packages/core/src/matcher_core/engine/Engine.py#41-52

### Properties :badge[Property]{variant=caution}
- `assembled -> bool` — `True` when all producer groups are present (`_pp`, `_gp`, `_sp`).
- `running -> bool` — indicates whether the engine loop currently holds the lock (i.e., actively processing).
@backend/packages/core/src/matcher_core/engine/Engine.py#54-60

### Configuration methods :badge[Method]{variant=tip}
- `set_source_producers(source_producers: list[Producer[np.ndarray]]) -> None`
- `set_gaze_producers(gaze_producers: list[Producer[tuple[float, float]]]) -> None`
- `set_scene_producer(scene_producer: Producer[np.ndarray]) -> None`
- `set_environment(source_producers: list[Producer[np.ndarray]], gaze_producers: list[Producer[tuple[float, float]]], scene_producer: Producer[np.ndarray]) -> None`
- `set_pipeline(fn: Pipeline) -> None`

Each method updates the corresponding dependency while ensuring the engine is paused and resumed safely.
@backend/packages/core/src/matcher_core/engine/Engine.py#62-90

### Internal helpers :badge[Method]{variant=caution}
- `_ctx(stack: AsyncExitStack) -> Awaitable[None]` — enters every producer's async context, logging readiness, and registers them on the shared exit stack.
- `_pass() -> Awaitable[None]` — assembles the payload, stamps it, runs the pipeline via `asyncer.asyncify`, and publishes either `result` or `error` events, yielding back to the event loop between passes.
- `_loop() -> Awaitable[None]` — owns the main processing while holding the lock; repeatedly invokes `_pass()` until cancelled.
@backend/packages/core/src/matcher_core/engine/Engine.py#91-118

### Control surface :badge[Method]{variant=tip}
- `halt() -> None` — cancels the task group scope, stopping the engine loop.
- `__call__(self, *args, **kwargs) -> bool` — starts the engine if it is assembled and not already running, scheduling `_loop()` on the task group. Returns `False` otherwise.
@backend/packages/core/src/matcher_core/engine/Engine.py#119-126
