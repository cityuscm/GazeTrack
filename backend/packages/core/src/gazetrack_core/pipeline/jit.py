from typing import Tuple

import cv2
import numpy as np
from numba import njit

from gazetrack_core.utils import PerspectiveTransformResult


@njit(cache=True, fastmath=True)
def is_valid_quadrilateral_numba(points: np.ndarray) -> bool:
    """
    Numba-accelerated version of quadrilateral validation.

    Args:
        points: Array of shape (4, 2) containing quadrilateral vertices

    Returns:
        bool: True if quadrilateral is convex (non-self-intersecting)
    """
    # Ensure we have the right shape
    if points.shape != (4, 2):
        return False

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


@njit(cache=True, fastmath=True)
def calculate_determinant_2x2(matrix: np.ndarray) -> float:
    """
    Calculate determinant of 2x2 matrix extracted from 3x3 perspective matrix.

    Args:
        matrix: 3x3 perspective transformation matrix

    Returns:
        float: Determinant of the upper-left 2x2 submatrix
    """
    return matrix[0, 0] * matrix[1, 1] - matrix[0, 1] * matrix[1, 0]


def check_perspective_transform_numba(
    src_points: np.ndarray, dst_points: np.ndarray
) -> Tuple[bool, PerspectiveTransformResult]:
    """
    Numba-accelerated version of perspective transform validation.

    This function accelerates the quadrilateral validation using numba
    while keeping OpenCV operations in regular Python.

    Args:
        src_points: Source quadrilateral points (4, 2)
        dst_points: Destination quadrilateral points (4, 2)

    Returns:
        Tuple[bool, PerspectiveTransformResult]: Validation result and reason
    """
    # Ensure arrays are properly shaped and typed to match non-numba version
    src_points_np = np.asarray(src_points, dtype=np.float32).reshape(4, 2)
    dst_points_np = np.asarray(dst_points, dtype=np.float32).reshape(4, 2)

    # Calculate transformation matrix using OpenCV (not numba-compatible)
    try:
        M = cv2.getPerspectiveTransform(src_points_np, dst_points_np)
    except cv2.error:
        return False, PerspectiveTransformResult.NEAR_SINGULAR_MATRIX

    # Check for near-singular matrix (very small determinant)
    # Use same determinant calculation as non-numba version
    det = np.linalg.det(M[:2, :2])
    if abs(det) < 1e-10:
        return False, PerspectiveTransformResult.NEAR_SINGULAR_MATRIX

    # Check if quadrilaterals are valid using numba-accelerated function
    # Convert to float64 for numba compatibility while maintaining same logic
    if not is_valid_quadrilateral_numba(src_points_np.astype(np.float64)):
        return False, PerspectiveTransformResult.SELF_INTERSECTING_QUADRILATERAL

    if not is_valid_quadrilateral_numba(dst_points_np.astype(np.float64)):
        return False, PerspectiveTransformResult.SELF_INTERSECTING_QUADRILATERAL

    return True, PerspectiveTransformResult.VALID


# Alternative fully-accelerated version for when OpenCV is not needed
@njit(cache=True, fastmath=True)
def is_valid_quadrilateral_only(
    src_points: np.ndarray, dst_points: np.ndarray
) -> Tuple[bool, int]:
    """
    Lightweight validation focusing only on quadrilateral validity.

    Returns:
        Tuple[bool, int]: (is_valid, error_code)
        error_code: 0=valid, 1=self_intersecting, 2=invalid_shape
    """
    # Check array shapes
    if src_points.shape != (4, 2) or dst_points.shape != (4, 2):
        return False, 2

    # Validate source quadrilateral
    if not is_valid_quadrilateral_numba(src_points):
        return False, 1

    # Validate destination quadrilateral
    if not is_valid_quadrilateral_numba(dst_points):
        return False, 1

    return True, 0
