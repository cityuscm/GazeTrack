from dataclasses import dataclass
from typing import Sequence

import cv2
import numpy as np


@dataclass
class MatchResult:
    @dataclass
    class KeyPointSet:
        a: Sequence[cv2.KeyPoint]
        b: Sequence[cv2.KeyPoint]

        def a_numpy(self):
            return np.array([p.pt for p in self.a])

        def b_numpy(self):
            return np.array([p.pt for p in self.b])

    keypoint: KeyPointSet
    matches: Sequence[cv2.DMatch]
    homography: np.ndarray

    @classmethod
    def of(
        cls,
        kp_a: Sequence[cv2.KeyPoint],
        kp_b: Sequence[cv2.KeyPoint],
        match: Sequence[cv2.DMatch],
        homography: np.ndarray,
    ):
        return MatchResult(
            keypoint=cls.KeyPointSet(a=kp_a, b=kp_b),
            matches=match,
            homography=homography,
        )

    def __len__(self):
        return len(self.matches)

    def __iter__(self):
        return iter((self.keypoint.a, self.keypoint.b, self.matches, self.homography))

    def pairs(self):
        arr = []
        for match in self.matches:
            idx_a = match.queryIdx
            idx_b = match.trainIdx

            kp_a = self.keypoint.a[idx_a]
            kp_b = self.keypoint.b[idx_b]

            arr.append((np.array(kp_a.pt), np.array(kp_b.pt)))
        return arr
