from typing import Protocol

from gazetrack_core.struct.PipelineStruct import (
    Payload,
    CompressedPayload,
    Intermediate,
    Matched,
    Validated,
    Final,
)
from gazetrack_core.struct.Timestamped import Timestamped


class PayloadCompressor(Protocol):
    def __call__(self, it: Payload) -> CompressedPayload: ...


class PayloadProcessor(Protocol):
    def __call__(self, it: CompressedPayload) -> Intermediate: ...


class PayloadMatcher(Protocol):
    def __call__(self, it: Intermediate) -> Matched: ...


class PayloadValidator(Protocol):
    def __call__(self, it: Matched) -> Validated: ...


class PayloadProjector(Protocol):
    def __call__(self, it: Validated) -> Final: ...


class Pipeline(Protocol):
    def __call__(self, it: Timestamped[Payload]) -> Timestamped[Final]: ...
