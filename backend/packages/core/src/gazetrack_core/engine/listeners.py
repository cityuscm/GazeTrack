import typing

from loguru import logger

from gazetrack_core.aggregator.impl import RTSPAggregator, NDIAggregator
from gazetrack_core.engine.Engine import Engine
from gazetrack_core.event.EventBus import EventBus
from gazetrack_core.utils.utils import unzip2
from gazetrack_web.api.model import Session


async def session_listener(
    bus: EventBus,
    engine: Engine,
    rtsp_aggregator: RTSPAggregator,
    ndi_aggregator: NDIAggregator,
):
    async with bus.subscribe("set_session") as stream:
        async for event in stream:
            payload = event.payload
            session = typing.cast(Session, payload)
            logger.info(session)
            logger.info(payload)
            client_producer, gaze_producer = unzip2(
                [rtsp_aggregator.get(cid) for cid in session.clients]
            )
            ndi_producer = ndi_aggregator.get(session.scene)
            if not client_producer or not gaze_producer or not ndi_producer:
                logger.error("Missing producer")
                continue
            await engine.set_environment(
                source_producers=client_producer,
                gaze_producers=gaze_producer,
                scene_producer=ndi_producer,
            )


async def control_listener(bus: EventBus, engine: Engine):
    async with bus.subscribe("control") as stream:
        async for event in stream:
            payload = event.payload
            run = typing.cast(bool, payload)
            engine() if run else engine.halt()
