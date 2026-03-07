import cv2
from loguru import logger
import numpy as np
import torch

from returns.result import Result, Success, Failure

from gazetrack_core.interface.feature import Feature2D, Feature
from gazetrack_core.pipeline.functions import (
    batch_resize,
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
    MatchData,
    Validated,
    Final,
    Projection,
)
from gazetrack_core.struct.Timestamped import Timestamped
from gazetrack_core.utils import unzip2, transform_points
from gazetrack_core.pipeline.exceptions import (
    PipelineError,
    ValidationError,
    ProcessingError,
    SafelyIgnoreableError,
)


def compress(payload: Payload) -> Result[CompressedPayload, Exception]:
    try:
        if not payload.visual:
            return Failure(ValidationError("Empty visual data in payload"))

        if len(payload.gaze) != len(payload.visual):
            return Failure(ValidationError("Mismatched visual and gaze data lengths"))

        if payload.scene is None or payload.scene.size == 0:
            return Failure(ValidationError("Empty scene data in payload"))

        visual_height, visual_width, _ = payload.visual[0].shape
        scene_height, scene_width, _ = payload.scene.shape

        target_size = 480
        visual_scale = target_size / min(visual_height, visual_width)
        scene_scale = target_size / min(scene_height, scene_width)

        compressed_visual = batch_resize(payload.visual, visual_scale, visual_scale)
        compressed_scene = cv2.resize(
            payload.scene,
            (int(scene_width * scene_scale), int(scene_height * scene_scale)),
        )

        return Success(
            CompressedPayload(
                visual=compressed_visual,
                gaze=payload.gaze,
                scene=compressed_scene,
                visual_scale=visual_scale,
                scene_scale=scene_scale,
            )
        )
    except (ValidationError, ProcessingError) as e:
        return Failure(e)
    except Exception as e:
        return Failure(ProcessingError(f"Unexpected error in compress: {str(e)}"))


def process(
    payload: CompressedPayload, model: Feature2D[Feature]
) -> Result[Intermediate, Exception]:
    try:
        if not payload.visual:
            return Failure(ValidationError("Empty visual data in payload"))

        if payload.scene is None or payload.scene.size == 0:
            return Failure(ValidationError("Empty scene data in payload"))

        num_visual = len(payload.visual)
        batch_size = min(4096, max(512, num_visual * 64))

        tensors = [torch.from_numpy(v).permute(2, 0, 1) for v in payload.visual]
        stack = torch.stack(tensors)

        kps = model.detectAndCompute(stack, top_k=batch_size)
        scene_result = model.detectAndCompute(payload.scene, top_k=batch_size)[0]

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

        del tensors, stack, kps, scene_result

        return Success(
            Intermediate(
                visual=visual,
                visual_image=payload.visual,
                gaze=payload.gaze,
                scene=scene,
                scene_image=payload.scene,
                visual_scale=payload.visual_scale,
                scene_scale=payload.scene_scale,
            )
        )
    except (ValidationError, ProcessingError) as e:
        return Failure(e)
    except Exception as e:
        return Failure(ProcessingError(f"Unexpected error in process: {str(e)}"))


def match(
    intermediate: Intermediate, model: Feature2D[Feature]
) -> Result[Matched, Exception]:
    try:
        if not intermediate.visual:
            return Failure(ValidationError("Empty visual features in intermediate"))

        scene_descriptors = intermediate.scene.descriptors
        scene_keypoints_cpu = intermediate.scene.keypoints.cpu().numpy()

        matches: list[MatchData] = []
        for feature in intermediate.visual:
            visual_idx, scene_idx = model.match(
                feature.descriptors, scene_descriptors, min_cossim=-1
            )

            if len(visual_idx) == 0:
                return Failure(ValidationError("No matches found for a visual feature"))

            visual_idx_cpu = visual_idx.cpu()
            scene_idx_cpu = scene_idx.cpu()
            visual_kps = feature.keypoints[visual_idx_cpu].cpu().numpy()
            scene_kps = scene_keypoints_cpu[scene_idx_cpu]
            matches.append(match_data_from_keypoints(visual_kps, scene_kps))

        del scene_keypoints_cpu

        return Success(
            Matched(
                match_data=matches,
                visual=intermediate.visual,
                visual_image=intermediate.visual_image,
                gaze=intermediate.gaze,
                scene=intermediate.scene,
                scene_image=intermediate.scene_image,
                visual_scale=intermediate.visual_scale,
                scene_scale=intermediate.scene_scale,
            )
        )
    except (ValidationError, ProcessingError) as e:
        return Failure(e)
    except Exception as e:
        match e:
            case cv2.error():  # Ignore OpenCV errors
                return Failure(
                    SafelyIgnoreableError(f"OpenCV error in match: {str(e)}")
                )
            case IndexError():  # Ignore pure black frames (empty arrays)
                return Failure(SafelyIgnoreableError(f"Index error in match: {str(e)}"))
            case _:
                return Failure(ProcessingError(f"Unexpected error in match: {str(e)}"))


def validate(matched: Matched) -> Result[Validated, Exception]:
    try:
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
        return Success(
            Validated(
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
        )
    except Exception as e:
        return Failure(e)


def project(validated: Validated) -> Result[Final, Exception]:
    try:
        projections: list[Projection] = []
        for i, valid in enumerate(validated.valid):
            if not valid:
                continue

            homography = validated.match_data[i].homography
            if homography is None:
                continue

            gaze = (
                np.array([validated.gaze[i][0], validated.gaze[i][1]], dtype=np.float32)
                * validated.visual_scale
            )

            point: np.ndarray = cv2.perspectiveTransform(
                gaze.reshape(-1, 1, 2), homography
            ).reshape(-1, 2)[0]

            scaled = point / validated.scene_scale
            bound = validated.scene_image.shape[1], validated.scene_image.shape[0]

            if not (0 <= scaled[0] <= bound[0]) or not (0 <= scaled[1] <= bound[1]):
                continue

            projections.append(
                Projection(
                    gaze=(float(scaled[0]), float(scaled[1])), bound=bound, index=i
                )
            )

        return Success(Final(projection=projections))
    except (ValidationError, ProcessingError) as e:
        return Failure(e)
    except Exception as e:
        return Failure(ProcessingError(f"Unexpected error in project: {str(e)}"))


def default_pipeline_from(model: Feature2D[Feature]) -> Pipeline:
    def pipeline(
        timestamped_payload: Timestamped[Payload],
    ) -> Result[Timestamped[Final], PipelineError]:
        time = timestamped_payload.timestamp
        # compress_result = compress(timestamped_payload.value)
        # process_result = compress_result.bind(lambda x: process(x, model))
        # match_result = process_result.bind(lambda x: match(x, model))
        # validate_result = match_result.bind(validate)
        # project_result = validate_result.bind(project)
        # final_result = project_result.bind(
        #     lambda final: Success(Timestamped(final, time))
        # )
        # return final_result

        return (
            compress(timestamped_payload.value)
            .bind(lambda x: process(x, model))
            .bind(lambda x: match(x, model))
            .bind(validate)
            .bind(project)
            .bind(lambda final: Success(Timestamped(final, time)))
        )

    return pipeline
