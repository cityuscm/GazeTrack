from typing import Callable

import cv2
import numpy as np
import torch

from DataContainer import MatchResult

type Matcher = Callable[[np.ndarray, np.ndarray], MatchResult]

def _xfeat_raw_to_match_result(kp_a, kp_b) -> MatchResult:
    if len(kp_a) <= 4 or len(kp_b) <= 4:
        return MatchResult.of([], [], [], np.eye(3))
    homography, mask = cv2.findHomography(
        kp_a, kp_b, cv2.USAC_MAGSAC, 3.5, maxIters=1_000, confidence=0.999
    )
    kp_a = [cv2.KeyPoint(p[0], p[1], 1) for p in kp_a]
    kp_b = [cv2.KeyPoint(p[0], p[1], 1) for p in kp_b]
    matches = [cv2.DMatch(i, i, 1) for i in range(len(kp_a)) if mask[i]]
    return MatchResult.of(kp_a, kp_b, matches, homography)


def xfeat_matcher(xfeat: torch.nn.Module, lg: bool = False) -> Matcher:
    def out(a: np.ndarray, b: np.ndarray) -> MatchResult:
        if lg:
            out_a = xfeat.detectAndCompute(a, top_k=xfeat.top_k)[0]
            out_b = xfeat.detectAndCompute(b, top_k=xfeat.top_k)[0]
            out_a.update({"image_size": (a.shape[1], a.shape[0])})
            out_b.update({"image_size": (b.shape[1], b.shape[0])})
            kp_a, kp_b = xfeat.match_lighterglue(out_a, out_b)[:2]
        else:
            kp_a, kp_b = xfeat.match_xfeat(a, b, top_k=xfeat.top_k)
        return _xfeat_raw_to_match_result(kp_a, kp_b)

    return out
