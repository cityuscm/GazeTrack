from contextlib import asynccontextmanager

import asyncer
from fastapi import FastAPI
from loguru import logger

from gazetrack_core.aggregator.impl import RTSPAggregator, NDIAggregator
from gazetrack_core.engine import Engine
from gazetrack_core.engine.listeners import (
    session_listener,
    control_listener,
)
from gazetrack_core.event import EventBus
from gazetrack_core.exporter import osc_exporter_from, ws_exporter_from
from gazetrack_core.exporter.listeners import exporter_listener_from
from gazetrack_core.pipeline import default_pipeline_from
from gazetrack_core.utils import get_model
from gazetrack_web.api.route.default import default_router
from gazetrack_web.api.ws.manager import GazeWebSocketManager
from gazetrack_web.api.ws.route import ws_router
from gazetrack_web.static import include_static


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting...")
    pipeline = default_pipeline_from(get_model())
    bus = EventBus()
    ws_manager = GazeWebSocketManager()
    async with (
        asyncer.create_task_group() as tg,
        RTSPAggregator() as rtsp_aggregator,
        NDIAggregator() as ndi_aggregator,
        Engine(fn=pipeline, bus=bus) as engine,
    ):
        osc_out = osc_exporter_from("127.0.0.1", 5001)
        ws_out = ws_exporter_from(ws_manager.broadcast)

        tg.soonify(session_listener)(bus, engine, rtsp_aggregator, ndi_aggregator)
        tg.soonify(control_listener)(bus, engine)
        tg.soonify(exporter_listener_from)(bus, osc_out)
        tg.soonify(exporter_listener_from)(bus, ws_out)

        router = default_router(
            lambda: rtsp_aggregator.sources,
            lambda: ndi_aggregator.sources,
            lambda: engine.running,
            bus,
        )
        app.include_router(router)
        app.include_router(ws_router(ws_manager))
        include_static(app)
        yield
        logger.info("Shutting down...")
        engine.halt()
        tg.cancel_scope.cancel()


app = FastAPI(lifespan=lifespan)
