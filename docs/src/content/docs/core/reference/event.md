---
title: Event
description: Event data structures and pub/sub contract used by the runtime.
sidebar:
  badge: { text: "Module", variant: "success" }
---

## Classes

### `Event` :badge[Class]{variant=note}
- **Module:** `packages.core.src.matcher_core.event.EventBus`
- **Signature:** `@dataclass class Event`
- **Fields:** `topic: str`, `payload: Any` — minimal envelope used across all matcher topics.
@backend/packages/core/src/matcher_core/event/EventBus.py#10-14

## Protocols

### `AbstractEventBus` :badge[Protocol]{variant=note}
- **Module:** `packages.core.src.matcher_core.event.EventBus`
- **Signature:** `class AbstractEventBus(Protocol)`
- **Methods:**
  - `subscribe(topic: str) -> AsyncObservable[Event]`
  - `publish(event: Event) -> None`
Defines the required interface for any event bus implementation so engines and listeners remain decoupled.@backend/packages/core/src/matcher_core/event/EventBus.py#16-18

## Implementations

### `EventBus` :badge[Class]{variant=note}
- **Module:** `packages.core.src.matcher_core.event.EventBus`
- **Signature:** `class EventBus(AbstractEventBus)`
- **Constructor:** `__init__(self)` — initializes internal `dict[str, AsyncSubject]` registry for topics.
- **Methods:**
  - `subscribe(topic: str) -> AsyncGenerator[AsyncIteratorObserver[Event], None]` — async context manager yielding an iterator observer filtered to the requested topic. Ensures subscription disposal when the context exits.
  - `publish(event: Event) -> None` — pushes the event to the topic’s subject if present.
@backend/packages/core/src/matcher_core/event/EventBus.py#21-44
