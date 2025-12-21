---
title: Pipeline
description: Stage protocols and reference implementations for transforming payloads into gaze projections.
sidebar:
  badge: { text: "Module", variant: "success" }
---

## Stage protocols (`matcher_core.pipeline.interfaces`)

### `PayloadCompressor` :badge[Protocol]{variant=note} :badge[SAM]{variant=tip}
```python
class PayloadCompressor(Protocol):
    def __call__(self, it: Payload) -> CompressedPayload: ...
```
Defines the contract for reducing image resolution while preserving scale factors.
@backend/packages/core/src/matcher_core/pipeline/interfaces.py#14-16

### `PayloadProcessor` :badge[Protocol]{variant=note} :badge[SAM]{variant=tip}
```python
def __call__(self, it: CompressedPayload) -> Intermediate: ...
```
Transforms compressed images into learned feature representations.
@backend/packages/core/src/matcher_core/pipeline/interfaces.py#18-19

### `PayloadMatcher` :badge[Protocol]{variant=note} :badge[SAM]{variant=tip}
```python
def __call__(self, it: Intermediate) -> Matched: ...
```
Consumes detector outputs and produces pairwise matches plus homographies.
@backend/packages/core/src/matcher_core/pipeline/interfaces.py#22-24

### `PayloadValidator` :badge[Protocol]{variant=note} :badge[SAM]{variant=tip}
```python
def __call__(self, it: Matched) -> Validated: ...
```
Filters invalid homographies and annotates each POV stream with a `valid` flag.
@backend/packages/core/src/matcher_core/pipeline/interfaces.py#26-27

### `PayloadProjector` :badge[Protocol]{variant=note} :badge[SAM]{variant=tip}
```python
def __call__(self, it: Validated) -> Final: ...
```
Reprojects gaze rays into scene coordinates and returns `Projection` structs.
@backend/packages/core/src/matcher_core/pipeline/interfaces.py#30-31

### `Pipeline` :badge[Protocol]{variant=note} :badge[SAM]{variant=tip}
```python
def __call__(self, it: Timestamped[Payload]) -> Timestamped[Final]: ...
```
General contract for any runnable pipeline implementation.
@backend/packages/core/src/matcher_core/pipeline/interfaces.py#34-35

## Reference stage implementations (`matcher_core.pipeline.pipeline`)

### `collect` :badge[Function]{variant=tip}
```python
def collect(session: Session) -> Timestamped[Payload]
```
Pulls the most recent POV/gaze/scene frames from a web session and wraps them in a timestamped payload.
@backend/packages/core/src/matcher_core/pipeline/pipeline.py#29-41

### `compress` :badge[Function]{variant=tip}
```python
def compress(payload: Payload) -> CompressedPayload
```
Resizes each POV frame and the scene image to a 480px minimum dimension and captures uniform scale factors for later reprojection.
@backend/packages/core/src/matcher_core/pipeline/pipeline.py#44-60

### `process` :badge[Function]{variant=tip}
```python
def process(payload: CompressedPayload, model: Feature2D[Feature]) -> Intermediate
```
Runs the supplied `Feature2D` detector, emitting `FeatureSet` tensors plus cached images and scale metadata.
@backend/packages/core/src/matcher_core/pipeline/pipeline.py#63-90

### `match` :badge[Function]{variant=tip}
```python
def match(intermediate: Intermediate, model: Feature2D[Feature]) -> Matched
```
Matches descriptors between each POV stream and the scene, producing `MatchData` entries per camera.
@backend/packages/core/src/matcher_core/pipeline/pipeline.py#92-115

### `validate` :badge[Function]{variant=tip}
```python
def validate(matched: Matched) -> Validated
```
Projects canonical quadrilaterals through the computed homographies and flags invalid transforms via `check_perspective_transform_numba`.
@backend/packages/core/src/matcher_core/pipeline/pipeline.py#118-140

### `project` :badge[Function]{variant=tip}
```python
def project(validated: Validated) -> Final
```
Converts normalized gaze coordinates into scene pixels using the validated homographies and builds the final `Projection` list.
@backend/packages/core/src/matcher_core/pipeline/pipeline.py#143-163

### `default_pipeline_from` :badge[Function]{variant=tip}
```python
def default_pipeline_from(model: Feature2D[Feature]) -> Pipeline
```
Returns a callable pipeline chaining `compress → process → match → validate → project` over timestamped payloads, preserving the timestamp throughout the transformation.
@backend/packages/core/src/matcher_core/pipeline/pipeline.py#166-175

## Supporting functions (`matcher_core.pipeline.functions`)

### `batch_resize` :badge[Function]{variant=tip}
```python
def batch_resize(images: list[np.ndarray], fx: float, fy: float) -> list[np.ndarray]
```
Attempts to resize all images in batch for efficiency; falls back to per-image resizing when memory limits are exceeded.
@backend/packages/core/src/matcher_core/pipeline/functions.py#7-28

### `match_data_from_keypoints` :badge[Function]{variant=tip}
```python
def match_data_from_keypoints(a: np.ndarray, b: np.ndarray) -> MatchData
```
Computes a homography and synthetic matches between two keypoint arrays using OpenCV’s USAC MAGSAC solver.
@backend/packages/core/src/matcher_core/pipeline/functions.py#31-58

### `quadrilateral_from_image` :badge[Function]{variant=tip}
```python
def quadrilateral_from_image(image: np.ndarray) -> np.ndarray
```
Produces the `[TL, TR, BR, BL]` corner coordinates for an image, used when validating perspective transforms.
@backend/packages/core/src/matcher_core/pipeline/functions.py#61-78
