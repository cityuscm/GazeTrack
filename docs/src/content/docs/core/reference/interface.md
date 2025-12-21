---
title: Interface
description: Protocols and typed dictionaries that define detector and functional contracts.
sidebar:
  badge: { text: "Module", variant: "success" }
---

## Module: `packages.core.src.matcher_core.interface.feature`

### `Feature` :badge[TypedDict]{variant=caution}
- **Signature:** `class Feature(TypedDict)`
- **Fields:**
  - `keypoints: torch.Tensor`
  - `scores: torch.Tensor`
  - `descriptors: torch.Tensor`
Represents the detector output for a single image, used by pipeline stages when interacting with `Feature2D` implementations.@backend/packages/core/src/matcher_core/interface/feature.py#7-11

### `Feature2D[T]` :badge[Protocol]{variant=note}
- **Signature:** `class Feature2D[T](Protocol)`
- **Methods:**
  - `detectAndCompute(x: Union[torch.Tensor, np.ndarray], top_k: Optional[int] = None, detection_threshold: Optional[float] = None) -> List[T]`
  - `detectAndComputeDense(x: Union[torch.Tensor, np.ndarray], top_k: Optional[int] = None, multiscale: bool = True) -> Dict[str, torch.Tensor]`
  - `match(feats1: torch.Tensor, feats2: torch.Tensor, min_cossim: float = 0.82) -> Tuple[torch.Tensor, torch.Tensor]`
  - `parse_input(x: Union[torch.Tensor, np.ndarray]) -> torch.Tensor`
Custom detector backends must implement these methods so the reference pipeline can request sparse/dense features and perform descriptor matching.@backend/packages/core/src/matcher_core/interface/feature.py#13-33

## Module: `packages.core.src.matcher_core.interface.functional`

### `PayloadAssembler` :badge[Protocol]{variant=note} :badge[SAM]{variant=tip}
- **Signature:** `class PayloadAssembler`
```python
def __call__(
  pov_producers: list[Producer[np.ndarray]],
  gaze_producers: list[Producer[tuple[float, float]]],
  scene_producer: Producer[np.ndarray],
) -> Payload
```
Protocol describing a callable that transforms active producers into a `Payload`. The concrete implementation is provided by `assemble_payload` and `PayloadProducer`.
@backend/packages/core/src/matcher_core/interface/functional.py#8-14

### `Timestamper[T]` :badge[Protocol]{variant=note} :badge[SAM]{variant=tip}
- **Signature:** `class Timestamper[T]`
```python
def __call__(data: T) -> Timestamped[T]
```
Represents a callable that annotates arbitrary data with a timestamp, implemented in practice by `stamp`.
@backend/packages/core/src/matcher_core/interface/functional.py#17-18
