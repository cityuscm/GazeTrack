from typing import Protocol, TypedDict, Union, Optional, List, Dict, Tuple

import numpy as np
import torch


class Feature(TypedDict):
    keypoints: torch.Tensor
    scores: torch.Tensor
    descriptors: torch.Tensor


class Feature2D[T](Protocol):
    def detectAndCompute(
        self,
        x: Union[torch.Tensor, np.ndarray],
        top_k: Optional[int] = None,
        detection_threshold: Optional[float] = None,
    ) -> List[T]: ...

    def detectAndComputeDense(
        self,
        x: Union[torch.Tensor, np.ndarray],
        top_k: Optional[int] = None,
        multiscale: bool = True,
    ) -> Dict[str, torch.Tensor]: ...

    def match(
        self, feats1: torch.Tensor, feats2: torch.Tensor, min_cossim: float = 0.82
    ) -> Tuple[torch.Tensor, torch.Tensor]: ...

    def parse_input(self, x: Union[torch.Tensor, np.ndarray]) -> torch.Tensor: ...
