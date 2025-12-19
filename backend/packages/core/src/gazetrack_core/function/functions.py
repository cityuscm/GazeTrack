import numpy as np

from gazetrack_core.producer.interface import Producer
from gazetrack_core.struct.PipelineStruct import Payload
from gazetrack_core.struct.Timestamped import Timestamped


def assemble_payload(
    pov_producers: list[Producer[np.ndarray]],
    gaze_producers: list[Producer[tuple[float, float]]],
    scene_producer: Producer[np.ndarray],
) -> Payload:
    return Payload(
        visual=[p.produce() for p in pov_producers],
        gaze=[p.produce() for p in gaze_producers],
        scene=scene_producer.produce(),
    )


def stamp[T](value: T) -> Timestamped[T]:
    return Timestamped(value)
