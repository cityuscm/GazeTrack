import contextlib
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Iterator, Callable

import aioreactive
import numpy as np
import torch
from aioreactive import AsyncObservable, AsyncAnonymousObserver
from aioreactive.subject import AsyncMultiSubject
from cyndilib import Finder
from expression.system import AsyncDisposable
from wireup import service, Injected

from DataContainer import Vec2, Vec2i, GazeProjection, Matchable, ClientInput
from type import ClientList
from util.transfrom import transform_points, check_perspective_transform, transform_point, resize_height, size
from util.xfeat import Matcher, xfeat_matcher


@service
async def merger_factory(
        c: Injected[AsyncMultiSubject[ClientInput]],
        s: Injected[AsyncMultiSubject[np.ndarray]],
        flow: Injected[AsyncMultiSubject[Matchable]]
) -> AsyncDisposable:
    it: AsyncObservable[tuple[ClientInput, np.ndarray]] = aioreactive.with_latest_from(c, s)

    async def f(x: tuple[ClientInput, np.ndarray]):
        flow.asend(Matchable(view=x[0].view, gaze=x[0].gaze, scene=x[1], id=x[0].id))

    return await it.subscribe_async(AsyncAnonymousObserver(f))


@service
def client_list_factory() -> ClientList:
    return ClientList({})


@service(lifetime="singleton")
def finder_factory() -> Iterator[Finder]:
    with contextlib.closing(Finder()) as finder:
        yield finder


@service
def executor_factory() -> ThreadPoolExecutor:
    return ThreadPoolExecutor(max_workers=1)


@service
def matcher_factory() -> Matcher:
    return xfeat_matcher(torch.hub.load(
        "verlab/accelerated_features", "XFeat", pretrained=True, top_k=4096
    ))


@service
def match_factory(
        matcher: Injected[Matcher]
) -> Callable[[tuple[tuple[np.ndarray, tuple[float, float]], np.ndarray]], GazeProjection | None]:
    def func(event: tuple[tuple[np.ndarray, tuple[float, float]], np.ndarray]):
        ((view, gaze), scene) = event
        scene_shape = scene.shape
        scene_vga = resize_height(scene, 480)
        view_vga = resize_height(view, 480)
        background_mult = 480 / scene.shape[0]
        target_mult = 480 / view.shape[0]
        original_gaze = np.array([gaze[0], gaze[1]])
        g = original_gaze * target_mult
        result = matcher(view_vga, scene_vga)
        original = size(view_vga).corners
        outline = transform_points(original, result.homography)
        valid, _ = check_perspective_transform(original, outline)
        if valid:
            absolute = transform_point(g, result.homography)
            absolute /= background_mult
            absolute = (float(absolute[0]), float(absolute[1]))
            return GazeProjection(
                Vec2i.from_cv(scene_shape),
                Vec2(*absolute),
            )
        else:
            return None

    return func
