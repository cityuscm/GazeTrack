---
title: Aggregator
description: Discovery helpers that create producer instances for POV, gaze, and scene sources.
sidebar:
  badge: { text: "Module", variant: "success" }
---

# Protocols

## `Aggregator[T]` :badge[Protocol]{variant=note}
- **Module:** `packages.core.src.matcher_core.aggregator.interface`
- **Signature:** `class Aggregator[T](Protocol)`
- **Members:**
  - `sources -> list[str]`: Enumerates the currently detected source identifiers.
  - `get(src: str) -> T`: Returns a producer instance for the selected source or raises if unavailable.
@backend/packages/core/src/matcher_core/aggregator/interface.py#1-8

### sources :badge[Property]{variant=caution} 
Enumerates the currently detected source identifiers.

### get :badge[Method]{variant=tip} 
Returns a producer instance for the selected source or raises if unavailable.

# Implementations

## `RTSPAggregator` :badge[Class]{variant=note}
- **Module:** `packages.core.src.matcher_core.aggregator.impl`
- **Signature:** `class RTSPAggregator(AsyncContextManagerMixin, Aggregator[tuple[RTSPProducer, GazeProducer]])`
- **Constructor:** `__init__(self) -> None` — initializes tracking maps for discovered Pupil Labs clients.
- **Context manager:** `__asynccontextmanager__(self) -> AsyncGenerator[Self, None]` — starts a background discovery task that scans for RTSP devices until the context exits.
- **Properties:**
  - `sources -> dict[str, url]` — read-only mapping of client address to paired world/gaze URLs.
- **Methods:**
  - `get(addr: str) -> tuple[RTSPProducer, GazeProducer]` — builds ready-to-use producers for the requested client, raising `ValueError` when the address is unknown.
@backend/packages/core/src/matcher_core/aggregator/impl.py#22-64

This aggregator discovers Pupil Labs RTSP streams automatically and pairs them with corresponding gaze data. It monitors for new Pupil Labs devices on the network and maintains mappings between world and gaze streams.

### sources :badge[Property]{variant=caution}
```python
sources: dict[str, url]
```

Read-only mapping of client address to paired world/gaze URLs.

### get :badge[Method]{variant=tip}
```python
get(addr: str) -> tuple[RTSPProducer, GazeProducer]
```
Returns a producer instance for the selected source or raises if unavailable.

## `NDIAggregator` :badge[Class]{variant=note}
- **Module:** `packages.core.src.matcher_core.aggregator.impl`
- **Signature:** `class NDIAggregator(AsyncContextManagerMixin, Aggregator[NDIProducer])`
- **Constructor:** `__init__(self, interval: float = 1.0)` — configures the polling cadence for NDI source discovery.
- **Context manager:** `__asynccontextmanager__(self) -> AsyncGenerator[Self, None]` — spawns a scanning loop that refreshes available NDI senders until cancelled.
- **Properties:**
  - `sources -> list[str]` — names of the currently visible NDI sources.
- **Methods:**
  - `get(src: str) -> NDIProducer` — returns an initialized producer for the chosen scene stream or raises when the finder is offline.
@backend/packages/core/src/matcher_core/aggregator/impl.py#66-99

This aggregator discovers NDI sources automatically and provides producers for them. It continuously scans for available NDI senders on the network.

### sources :badge[Property]{variant=caution}
```python
sources: list[str]
```

Read-only list of currently detected NDI source names.

### get :badge[Method]{variant=tip}
```python
get(src: str) -> NDIProducer
```
Returns a producer instance for the selected source or raises if unavailable.
