import numpy as np

from gazetrack_core.producer.interface import Producer
from gazetrack_core.struct.PipelineStruct import Payload
from gazetrack_core.struct.Timestamped import Timestamped


class PayloadAssembler:
    def __call__(
        self,
        pov_producers: list[Producer[np.ndarray]],
        gaze_producers: list[Producer[tuple[float, float]]],
        scene_producer: Producer[np.ndarray],
    ) -> Payload: ...


class Timestamper[T]:
    def __call__(self, data: T) -> Timestamped[T]: ...
