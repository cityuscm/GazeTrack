from typing import Protocol

from returns.result import Result

from gazetrack_core.struct.PipelineStruct import (
    Payload,
    CompressedPayload,
    Intermediate,
    Matched,
    Validated,
    Final,
)
from gazetrack_core.struct.Timestamped import Timestamped


class PayloadCollector(Protocol):
    def __call__(self, session) -> Result[Timestamped[Payload], Exception]: ...


class PayloadCompressor(Protocol):
    def __call__(self, payload: Payload) -> Result[CompressedPayload, Exception]: ...


class PayloadProcessor(Protocol):
    def __call__(
        self, payload: CompressedPayload, model
    ) -> Result[Intermediate, Exception]: ...


class PayloadMatcher(Protocol):
    def __call__(
        self, intermediate: Intermediate, model
    ) -> Result[Matched, Exception]: ...


class PayloadValidator(Protocol):
    def __call__(self, matched: Matched) -> Result[Validated, Exception]: ...


class PayloadProjector(Protocol):
    def __call__(self, validated: Validated) -> Result[Final, Exception]: ...


class Pipeline(Protocol):
    def __call__(
        self, timestamped_payload: Timestamped[Payload]
    ) -> Result[Timestamped[Final], Exception]: ...
