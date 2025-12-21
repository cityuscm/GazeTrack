---
title: Struct
description: Immutable containers and math helpers shared across the matcher pipeline.
sidebar:
  badge: { text: "Module", variant: "success" }
---

## Classes

### `Timestamped[T]` :badge[Class]{variant=note}
- **Module:** `packages.core.src.matcher_core.struct.Timestamped`
- **Signature:** `@frozen class Timestamped[T]`
- **Fields:**
  - `value: T` — wrapped payload.
  - `timestamp: float = time.time()` — capture instant assigned at construction.
- **Methods:**
  - `map(f: Callable[[T], U]) -> Timestamped[U]` — returns a new wrapper with the same timestamp but transformed value.
  - `unwrap() -> T` — returns the stored payload.
@backend/packages/core/src/matcher_core/struct/Timestamped.py#1-17

### `FeatureSet` :badge[Class]{variant=note}
- **Module:** `packages.core.src.matcher_core.struct.PipelineStruct`
- **Signature:** `@define class FeatureSet`
- **Fields:** `keypoints: torch.Tensor`, `scores: torch.Tensor`, `descriptors: torch.Tensor` — detector outputs for a single frame.
@backend/packages/core/src/matcher_core/struct/PipelineStruct.py#7-12

### `MatchData` :badge[Class]{variant=note}
- **Fields:**
  - `keypoints_a: list[cv2.KeyPoint]`
  - `keypoints_b: list[cv2.KeyPoint]`
  - `homography: np.ndarray`
  - `matches: list[cv2.DMatch]`
Represents correspondences and the homography between a POV frame and the scene.
@backend/packages/core/src/matcher_core/struct/PipelineStruct.py#15-20

### Pipeline payload hierarchy :badge[Struct]{variant=caution}
These attrs form the contract between every stage:

| Class | Key fields |
| --- | --- |
| `Payload` | `visual: list[np.ndarray]`, `gaze: list[tuple[float, float]]`, `scene: np.ndarray` |
| `CompressedPayload` | `visual`, `gaze`, `scene`, `visual_scale: float`, `scene_scale: float` |
| `Intermediate` | `visual: list[FeatureSet]`, `visual_image`, `gaze`, `scene: FeatureSet`, `scene_image`, `visual_scale`, `scene_scale` |
| `Matched` | `visual`, `visual_image`, `match_data: list[MatchData]`, `gaze`, `scene`, `scene_image`, `visual_scale`, `scene_scale` |
| `Validated` | `visual`, `visual_image`, `match_data`, `gaze`, `valid: list[bool]`, `scene`, `scene_image`, `visual_scale`, `scene_scale` |
| `Final` | `projection: list[Projection]` |
| `Projection` | `index: int`, `bound: tuple[int, int]`, `gaze: tuple[float, float]` |
@backend/packages/core/src/matcher_core/struct/PipelineStruct.py#23-84

## Functions

### `out_of_bound` :badge[Function]{variant=tip}
```python
def out_of_bound(projection: Projection) -> bool
```
Returns `True` when the projected gaze lies outside its bounding image.
@backend/packages/core/src/matcher_core/struct/functions.py#7-13

### `center_offset` :badge[Function]{variant=tip}
```python
def center_offset(projection: Projection) -> tuple[float, float]
```
Maps absolute gaze coordinates into a normalized offset in `[-0.5, 0.5]` space for both axes.
@backend/packages/core/src/matcher_core/struct/functions.py#16-21

### `center_offset_safe` :badge[Function]{variant=tip}
```python
def center_offset_safe(projection: Projection) -> Result[tuple[float, float], None]
```
Wraps `center_offset` in a Result, returning `Failure(None)` when the point is out of bounds.
@backend/packages/core/src/matcher_core/struct/functions.py#24-27

### `absolute_safe` :badge[Function]{variant=tip}
```python
def absolute_safe(projection: Projection) -> Result[tuple[float, float], None]
```
Returns the raw gaze tuple or `Failure(None)` if it falls outside the bounding box.
@backend/packages/core/src/matcher_core/struct/functions.py#30-33

### `normalized` :badge[Function]{variant=tip}
```python
def normalized(projection: Projection) -> tuple[float, float]
```
Expresses the gaze as values in `[0, 1]` by dividing by `bound`.
@backend/packages/core/src/matcher_core/struct/functions.py#36-39
