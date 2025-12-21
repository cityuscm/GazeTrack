---
title: Runtime helpers
description: Functional helpers for assembling payloads and attaching timestamps.
sidebar:
  badge: { text: "Module", variant: "success" }
---

## Functions (`packages.core.src.matcher_core.function.functions`)

### `assemble_payload` :badge[Function]{variant=tip}
- **Signature:**
```python
def assemble_payload(
    pov_producers: list[Producer[np.ndarray]],
    gaze_producers: list[Producer[tuple[float, float]]],
    scene_producer: Producer[np.ndarray],
) -> Payload
```
- **Behavior:** Invokes each POV/gaze producer synchronously, reads the latest scene frame, and returns a `Payload` containing aggregated data for all streams.
- **Use cases:** Quickly bridge a set of producers into the pipeline without instantiating `PayloadProducer` or the engine.
@backend/packages/core/src/matcher_core/function/functions.py#1-17

### `stamp` :badge[Function]{variant=tip}
- **Signature:**
```python
def stamp[T](value: T) -> Timestamped[T]
```
- **Behavior:** Wraps any value together with `time.time()` into a `Timestamped` container. Useful for preserving capture time before running through the pipeline.
@backend/packages/core/src/matcher_core/function/functions.py#20-21
