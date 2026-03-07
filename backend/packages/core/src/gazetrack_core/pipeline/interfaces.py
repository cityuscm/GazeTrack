from typing import Protocol

from gazetrack_core.pipeline.exceptions import PipelineError
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
    def __call__(self, session) -> Result[Timestamped[Payload], PipelineError]: ...


class PayloadCompressor(Protocol):
    def __call__(
        self, payload: Payload
    ) -> Result[CompressedPayload, PipelineError]: ...


class PayloadProcessor(Protocol):
    def __call__(
        self, payload: CompressedPayload, model
    ) -> Result[Intermediate, PipelineError]: ...


class PayloadMatcher(Protocol):
    def __call__(
        self, intermediate: Intermediate, model
    ) -> Result[Matched, PipelineError]: ...


class PayloadValidator(Protocol):
    def __call__(self, matched: Matched) -> Result[Validated, PipelineError]: ...


class PayloadProjector(Protocol):
    def __call__(self, validated: Validated) -> Result[Final, PipelineError]: ...


class Pipeline(Protocol):
    def __call__(
        self, timestamped_payload: Timestamped[Payload]
    ) -> Result[Timestamped[Final], PipelineError]: ...
