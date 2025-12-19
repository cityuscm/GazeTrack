import contextlib
from abc import ABC
from typing import IO, cast

import torch
from loguru import logger

from gazetrack_core.interface.feature import Feature2D, Feature


def get_model() -> Feature2D[Feature]:
    class StreamToLogger(IO, ABC):
        def __init__(self, level="INFO"):
            self._level = level

        def write(self, buffer):
            for line in buffer.rstrip().splitlines():
                logger.opt(depth=1).log(self._level, line.rstrip())

        def flush(self):
            pass

    stream = StreamToLogger()
    with contextlib.redirect_stderr(stream):
        model = torch.hub.load(
            "verlab/accelerated_features", "XFeat", pretrained=True, top_k=4096
        )
        return model


def unzip2[T, U](tuples: list[tuple[T, U]]) -> tuple[list[T], list[U]]:
    return cast(tuple[list[T], list[U]], cast(object, zip(*tuples)))
