from enum import Enum

import cv2
import numpy as np


def transform_points(points: np.ndarray, homography: np.ndarray) -> np.ndarray:
    return cv2.perspectiveTransform(points.reshape(-1, 1, 2), homography).reshape(-1, 2)


class PerspectiveTransformResult(Enum):
    NEAR_SINGULAR_MATRIX = "Near-singular transformation matrix"
    SELF_INTERSECTING_QUADRILATERAL = "Self-intersecting quadrilateral detected"
    VALID = "Valid transformation"
