import cv2
import numpy as np
import torch
from attrs import define


@define
class FeatureSet:
    keypoints: torch.Tensor
    scores: torch.Tensor
    descriptors: torch.Tensor


@define
class MatchData:
    keypoints_a: list[cv2.KeyPoint]
    keypoints_b: list[cv2.KeyPoint]
    homography: np.ndarray
    matches: list[cv2.DMatch]


@define
class Payload:
    visual: list[np.ndarray]
    gaze: list[tuple[float, float]]
    scene: np.ndarray


@define
class CompressedPayload:
    visual: list[np.ndarray]
    gaze: list[tuple[float, float]]
    scene: np.ndarray
    visual_scale: float
    scene_scale: float


@define
class Intermediate:
    visual: list[FeatureSet]
    visual_image: list[np.ndarray]
    gaze: list[tuple[float, float]]
    scene: FeatureSet
    scene_image: np.ndarray
    visual_scale: float
    scene_scale: float


@define
class Matched:
    visual: list[FeatureSet]
    visual_image: list[np.ndarray]
    match_data: list[MatchData]
    gaze: list[tuple[float, float]]
    scene: FeatureSet
    scene_image: np.ndarray
    visual_scale: float
    scene_scale: float


@define
class Validated:
    visual: list[FeatureSet]
    visual_image: list[np.ndarray]
    match_data: list[MatchData]
    gaze: list[tuple[float, float]]
    valid: list[bool]
    scene: FeatureSet
    scene_image: np.ndarray
    visual_scale: float
    scene_scale: float


@define
class Projection:
    index: int
    bound: tuple[int, int]
    gaze: tuple[float, float]


@define
class Final:
    projection: list[Projection]
