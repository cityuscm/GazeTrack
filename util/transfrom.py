from enum import Enum

import cv2
import numpy as np

from DataContainer.containers import ImageDimensions


def transform_point(point: np.ndarray, homography: np.ndarray) -> np.ndarray:
    return cv2.perspectiveTransform(
        np.array([point[0], point[1]], dtype=np.float32).reshape(-1, 1, 2), homography
    ).reshape(-1, 2)[0]


def transform_points(points: np.ndarray, homography: np.ndarray) -> np.ndarray:
    return cv2.perspectiveTransform(points.reshape(-1, 1, 2), homography).reshape(-1, 2)


class PerspectiveTransformResult(Enum):
    NEAR_SINGULAR_MATRIX = "Near-singular transformation matrix"
    SELF_INTERSECTING_QUADRILATERAL = "Self-intersecting quadrilateral detected"
    VALID = "Valid transformation"


def check_perspective_transform(
        src_points: np.ndarray, dst_points: np.ndarray
) -> tuple[bool, PerspectiveTransformResult]:
    # Check if quadrilaterals are valid (non-self-intersecting)
    def is_valid_quadrilateral(points):
        # Convert to numpy array if not already
        points = np.array(points).reshape(4, 2)

        # Check if the quadrilateral is convex
        # In a convex quadrilateral, all interior angles are less than 180 degrees
        sign = 0
        for i in range(4):
            p1 = points[i]
            p2 = points[(i + 1) % 4]
            p3 = points[(i + 2) % 4]

            # Calculate cross product
            dx1 = p2[0] - p1[0]
            dy1 = p2[1] - p1[1]
            dx2 = p3[0] - p2[0]
            dy2 = p3[1] - p2[1]
            cross = dx1 * dy2 - dy1 * dx2

            # Check sign consistency
            if i == 0:
                sign = 1 if cross > 0 else -1
            elif (cross > 0 > sign) or (cross < 0 < sign):
                return False

        return True

    # Calculate transformation matrix
    M = cv2.getPerspectiveTransform(src_points, dst_points)

    # Check for near-singular matrix (very small determinant)
    det = np.linalg.det(M[:2, :2])
    if abs(det) < 1e-10:
        return False, PerspectiveTransformResult.NEAR_SINGULAR_MATRIX

    # Check if quadrilaterals are valid
    if not is_valid_quadrilateral(src_points) or not is_valid_quadrilateral(dst_points):
        return False, PerspectiveTransformResult.SELF_INTERSECTING_QUADRILATERAL

    return True, PerspectiveTransformResult.VALID


def size(img: np.ndarray) -> ImageDimensions:
    return ImageDimensions(width=img.shape[1], height=img.shape[0])


def resize_height(img: np.ndarray, height: int) -> np.ndarray:
    (h, w) = img.shape[:2]
    r = float(height) / h
    dim = (int(w * r), height)
    return cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
