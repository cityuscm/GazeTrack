import cv2
import numpy as np
import torch

from gazetrack_core.interface.feature import Feature2D, Feature
from gazetrack_core.pipeline.functions import (
    match_data_from_keypoints,
    quadrilateral_from_image,
)
from gazetrack_core.pipeline.interfaces import Pipeline
from gazetrack_core.pipeline.jit import (
    check_perspective_transform_numba,
)
from gazetrack_core.struct.PipelineStruct import (
    FeatureSet,
    Payload,
    CompressedPayload,
    Intermediate,
    Matched,
    Validated,
    Final,
    Projection,
)
from gazetrack_core.struct.Timestamped import Timestamped
from gazetrack_core.utils import unzip2, transform_points
from gazetrack_web.api.model import Session


def collect(session: Session) -> Timestamped[Payload]:
    latest_input = [(visual.get(), gaze.get()) for visual, gaze in session.eye_tracker]
    latest_visual = [visual for visual, _ in latest_input]
    latest_gaze = [gaze for _, gaze in latest_input]
    latest_scene = session.scene.get()

    return Timestamped(
        Payload(
            visual=latest_visual,
            gaze=latest_gaze,
            scene=latest_scene,
        )
    )


def compress(payload: Payload) -> CompressedPayload:
    visual_height, visual_width, _ = payload.visual[0].shape
    scene_height, scene_width, _ = payload.scene.shape
    visual_scale = 480 / min(visual_height, visual_width)
    scene_scale = 480 / min(scene_height, scene_width)
    compressed_visual = [
        cv2.resize(visual, (0, 0), fx=visual_scale, fy=visual_scale)
        for visual in payload.visual
    ]
    compressed_scene = cv2.resize(payload.scene, (0, 0), fx=scene_scale, fy=scene_scale)
    return CompressedPayload(
        visual=compressed_visual,
        gaze=payload.gaze,
        scene=compressed_scene,
        visual_scale=visual_scale,
        scene_scale=scene_scale,
    )


def process(payload: CompressedPayload, model: Feature2D[Feature]) -> Intermediate:
    tensors = [torch.from_numpy(visual).permute(2, 0, 1) for visual in payload.visual]
    stack = torch.stack(tensors)
    kps = model.detectAndCompute(stack, top_k=4096)
    scene_result = model.detectAndCompute(payload.scene, top_k=4096)[0]
    visual = [
        FeatureSet(
            keypoints=kp["keypoints"],
            scores=kp["scores"],
            descriptors=kp["descriptors"],
        )
        for kp in kps
    ]
    scene = FeatureSet(
        keypoints=scene_result["keypoints"],
        scores=scene_result["scores"],
        descriptors=scene_result["descriptors"],
    )
    return Intermediate(
        visual=visual,
        visual_image=payload.visual,
        gaze=payload.gaze,
        scene=scene,
        scene_image=payload.scene,
        visual_scale=payload.visual_scale,
        scene_scale=payload.scene_scale,
    )


def match(intermediate: Intermediate, model: Feature2D[Feature]) -> Matched:
    visual_indices, scenes_indices = unzip2(
        [
            model.match(v.descriptors, intermediate.scene.descriptors, min_cossim=-1)
            for v in intermediate.visual
        ]
    )
    matches = [
        match_data_from_keypoints(
            feature.keypoints[visual_indices[i]].cpu().numpy(),
            intermediate.scene.keypoints[scenes_indices[i]].cpu().numpy(),
        )
        for i, feature in enumerate(intermediate.visual)
    ]
    return Matched(
        match_data=matches,
        visual=intermediate.visual,
        visual_image=intermediate.visual_image,
        gaze=intermediate.gaze,
        scene=intermediate.scene,
        scene_image=intermediate.scene_image,
        visual_scale=intermediate.visual_scale,
        scene_scale=intermediate.scene_scale,
    )


def validate(matched: Matched) -> Validated:
    quads = [quadrilateral_from_image(image) for image in matched.visual_image]
    transformed = [
        transform_points(quads[i], matched.match_data[i].homography)
        for i in range(len(matched.visual_image))
    ]
    valid, _ = unzip2(
        [
            check_perspective_transform_numba(quads[i], transformed[i])
            for i in range(len(matched.visual_image))
        ]
    )
    return Validated(
        visual=matched.visual,
        visual_image=matched.visual_image,
        match_data=matched.match_data,
        gaze=matched.gaze,
        valid=valid,
        scene=matched.scene,
        scene_image=matched.scene_image,
        visual_scale=matched.visual_scale,
        scene_scale=matched.scene_scale,
    )


def project(validated: Validated) -> Final:
    projections: list[Projection] = []
    for i, valid in enumerate(validated.valid):
        if valid:
            gaze = (
                np.array([validated.gaze[i][0], validated.gaze[i][1]], dtype=np.float32)
                * validated.visual_scale
            )
            point: np.ndarray = cv2.perspectiveTransform(
                gaze.reshape(-1, 1, 2), validated.match_data[i].homography
            ).reshape(-1, 2)[0]
            scaled = point / validated.scene_scale
            bound = validated.scene_image.shape[1], validated.scene_image.shape[0]
            projections.append(
                Projection(
                    gaze=(float(scaled[0]), float(scaled[1])), bound=bound, index=i
                )
            )
    return Final(
        projection=projections,
    )


def default_pipeline_from(model: Feature2D[Feature]) -> Pipeline:
    def pipeline(timestamped_payload: Timestamped[Payload]) -> Timestamped[Final]:
        return (
            timestamped_payload.map(compress)
            .map(lambda x: process(x, model))
            .map(lambda x: match(x, model))
            .map(validate)
            .map(project)
        )

    return pipeline
