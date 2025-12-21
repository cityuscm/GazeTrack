---
title: Producers
description: Streaming data sources that feed the matcher pipeline.
sidebar:
  badge: { text: "Module", variant: "success" }
---

## Protocols

### `Producer[T]` :badge[Protocol]{variant=note} :badge[SAM]{variant=tip}
- **Module:** `packages.core.src.matcher_core.producer.interface`
```python
class Producer[T](Protocol):
    def produce(self) -> T: ...
```
- **Behavior:** Returns the latest value from a streaming source. Implementations are expected to be thread-safe since the engine polls them concurrently.
@backend/packages/core/src/matcher_core/producer/interface.py#1-5

## Classes

### `PayloadProducer` :badge[Class]{variant=note}
- **Module:** `packages.core.src.matcher_core.producer.impl`
- **Signature:** `class PayloadProducer(Producer[Timestamped[Payload]])`
- **Purpose:** Bridges a set of POV/gaze producers and a scene producer into a single `Timestamped[Payload]` stream consumable by the pipeline.
@backend/packages/core/src/matcher_core/producer/impl.py#1-18

#### Constructor :badge[Method]{variant=tip}
```python
def __init__(
    self,
    scene_producer: Producer[np.ndarray],
    client_producer: list[tuple[Producer[np.ndarray], Producer[tuple[float, float]]]],
) -> None
```
- `scene_producer` — provides the latest scene frame.
- `client_producer` — list of `(pov, gaze)` producer tuples, one per headset.
@backend/packages/core/src/matcher_core/producer/impl.py#19-27

#### Methods :badge[Method]{variant=tip}
```python
def produce(self) -> Timestamped[Payload]
```
- Synchronously snapshots every producer and returns a timestamped payload that the pipeline can ingest directly.
@backend/packages/core/src/matcher_core/producer/impl.py#29-37

### `RTSPProducer` :badge[Class]{variant=note}
- **Module:** `packages.core.src.matcher_core.producer.impl`
- **Signature:** `class RTSPProducer(AsyncContextManagerMixin, Producer[np.ndarray])`
- **Purpose:** Streams video frames from an RTSP endpoint into the matcher pipeline.
@backend/packages/core/src/matcher_core/producer/impl.py#39-48

#### Constructor :badge[Method]{variant=tip}
```python
def __init__(self, url: str) -> None
```
- Stores the RTSP endpoint and prepares the async reader.
@backend/packages/core/src/matcher_core/producer/impl.py#40-44

#### Context manager :badge[Method]{variant=caution} :badge[Async]{variant=caution}
```python
async def __asynccontextmanager__(self) -> AsyncGenerator["RTSPProducer", None]
```
- Spawns a background task that continuously reads frames via `receive_video_frames` and tears it down automatically on exit.
@backend/packages/core/src/matcher_core/producer/impl.py#45-57

#### Methods :badge[Method]{variant=tip}
```python
def produce(self) -> np.ndarray
```
- Returns the most recently decoded BGR frame. Ensure the async context has started before calling to avoid `None` frames.
@backend/packages/core/src/matcher_core/producer/impl.py#59-63

### `GazeProducer` :badge[Class]{variant=note}
- **Module:** `packages.core.src.matcher_core.producer.impl`
- **Signature:** `class GazeProducer(AsyncContextManagerMixin, Producer[tuple[float, float]])`
- **Purpose:** Consumes gaze data from a streaming endpoint and exposes the latest `(x, y)` sample.
@backend/packages/core/src/matcher_core/producer/impl.py#65-74

#### Constructor :badge[Method]{variant=tip}
```python
def __init__(self, url: str) -> None
```
- Stores the gaze data endpoint and configures internal state.
@backend/packages/core/src/matcher_core/producer/impl.py#66-69

#### Context manager :badge[Method]{variant=caution}
```python
async def __asynccontextmanager__(self) -> AsyncGenerator["GazeProducer", None]
```
- Maintains a background listener via `receive_gaze_data` until cancelled.
@backend/packages/core/src/matcher_core/producer/impl.py#70-79

#### Methods :badge[Method]{variant=tip}
```python
def produce(self) -> tuple[float, float]
```
- Returns the last `(x, y)` normalized gaze vector.
@backend/packages/core/src/matcher_core/producer/impl.py#81-85

### `NDIProducer` :badge[Class]{variant=note}
- **Module:** `packages.core.src.matcher_core.producer.impl`
- **Signature:** `class NDIProducer(AsyncContextManagerMixin, Producer[np.ndarray])`
- **Purpose:** Connects to an NDI source and exposes the most recent RGB frame.
@backend/packages/core/src/matcher_core/producer/impl.py#87-101

#### Constructor :badge[Method]{variant=tip}
```python
def __init__(self, src: Source) -> None
```
- Accepts an NDI source descriptor and prepares retry/backoff state.
@backend/packages/core/src/matcher_core/producer/impl.py#88-94

#### Context manager :badge[Method]{variant=caution}
```python
async def __asynccontextmanager__(self) -> AsyncGenerator["NDIProducer", None]
```
- Connects to the source, sets up the receiver, and launches a fetch loop that keeps `_frame` fresh at the native frame rate.
@backend/packages/core/src/matcher_core/producer/impl.py#95-140

#### Methods :badge[Method]{variant=tip}
```python
def produce(self) -> np.ndarray
```
- Returns the latest captured RGB frame (shape `H x W x 3`). Ensure the context manager is active so `_ready` has been signaled.
@backend/packages/core/src/matcher_core/producer/impl.py#142-160
