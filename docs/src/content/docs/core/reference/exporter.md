---
title: Exporter
description: Event bus contract, exporter protocol, and built-in listeners.
sidebar:
  badge: { text: "Module", variant: "success" }
---

## Event bus

The exporter module builds on the runtime event bus types:

- `Event`
- `AbstractEventBus`
- `EventBus`

For full field and method documentation of these types, see the dedicated [Event](../event) reference page.

## Exporter protocol

### `Exporter[T]` :badge[Protocol]{variant=note} :badge[SAM]{variant=tip}
- **Module:** `packages.core.src.matcher_core.exporter.interface`
```python
class Exporter[T](Protocol):
    def __call__(self, value: T) -> None: ...
```
- **Behavior:** Stateless callable invoked for every outgoing payload.
@backend/packages/core/src/matcher_core/exporter/interface.py#1-5

## Listeners

### `exporter_listener_from` :badge[Function]{variant=tip} :badge[Async]{variant=caution}
- **Module:** `packages.core.src.matcher_core.exporter.listeners`
- **Signature:** `async def exporter_listener_from[T](bus: EventBus, exporter: Exporter[T]) -> None`
- **Behavior:** Subscribes to the `result` topic on the provided `EventBus`, iterates over the stream, and forwards each payload into the exporter callable.
@backend/packages/core/src/matcher_core/exporter/listeners.py#1-9

## Built-in exporters

### `osc_exporter_from` :badge[Function]{variant=tip}
- **Module:** `packages.core.src.matcher_core.exporter.exporters`
- **Signature:** `def osc_exporter_from(addr: str, port: int) -> Exporter[Timestamped[Final]]`
- **Behavior:**
  - Creates a `SimpleUDPClient` targeting `(addr, port)`.
  - Returns a closure that unwraps each `Timestamped[Final]`, iterates projections, and emits OSC messages under `/gaze/{index}` and `/offset/{index}` with absolute gaze coordinates and center offsets.
@backend/packages/core/src/matcher_core/exporter/exporters.py#1-19
