import cv2
import numpy as np

from gazetrack_core.struct.PipelineStruct import MatchData


def batch_resize(images: list[np.ndarray], fx: float, fy: float) -> list[np.ndarray]:
    """
    Attempt to resize a list of images in batch, if not possible, resize each image individually.
    Args:
        images: List of images to resize
        fx: Scale factor in x direction
        fy: Scale factor in y direction
    Returns:
        list[np.ndarray]: List of resized images
    """
    batch = np.stack(images)
    (n, h, w, c) = batch.shape
    batchable = (n * c) <= 512
    if batchable:
        pack = batch.transpose((1, 2, 3, 0)).reshape((h, w, c * n))
        resized = cv2.resize(pack, (0, 0), fx=fx, fy=fy)
        unpack = resized.reshape((int(h * fy), int(w * fx), c, n)).transpose(
            (3, 0, 1, 2)
        )
        return [unpack[i] for i in range(n)]
    else:
        return [cv2.resize(image, (0, 0), fx=fx, fy=fy) for image in images]


def match_data_from_keypoints(a: np.ndarray, b: np.ndarray):
    """
    Find homography and matches between two sets of keypoints.
    Args:
        a: Array of keypoints in the first image
        b: Array of keypoints in the second image
    Returns:
        MatchData: Match data containing homography and matches
    """
    # if len(a) <= 4 or len(b) <= 4:
    #     return MatchData(
    #         keypoints_a=[],
    #         keypoints_b=[],
    #         homography=np.eye(3),
    #         matches=[],
    #     )
    homography, mask = cv2.findHomography(
        a, b, cv2.USAC_MAGSAC, 3.5, maxIters=1_000, confidence=0.999
    )
    kp_a = [cv2.KeyPoint(p[0], p[1], 1) for p in a]
    kp_b = [cv2.KeyPoint(p[0], p[1], 1) for p in b]
    matches = [cv2.DMatch(i, i, 1) for i in range(len(kp_a)) if mask[i]]
    return MatchData(
        keypoints_a=kp_a,
        keypoints_b=kp_b,
        homography=homography,
        matches=matches,
    )


def quadrilateral_from_image(image: np.ndarray) -> np.ndarray:
    """
    Create a quadrilateral from an image.

    Args:
        image: Image to create quadrilateral from

    Returns:
        np.ndarray: Array of shape (4, 2) containing quadrilateral vertices
    """
    return np.float32(
        [
            np.array([0, 0]),
            np.array([image.shape[1], 0]),
            np.array([image.shape[1], image.shape[0]]),
            np.array([0, image.shape[0]]),
        ]
    )
