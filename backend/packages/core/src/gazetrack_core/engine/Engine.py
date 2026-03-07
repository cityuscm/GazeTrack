from contextlib import asynccontextmanager, AsyncExitStack
from typing import Callable, AsyncGenerator, Self, Optional
import time
import threading
from dataclasses import dataclass

import anyio
import asyncer
import numpy as np
from anyio import AsyncContextManagerMixin
from loguru import logger
from returns.result import Success, Failure

from gazetrack_core.event.EventBus import EventBus, Event
from gazetrack_core.function.functions import assemble_payload, stamp
from gazetrack_core.pipeline.interfaces import Pipeline
from gazetrack_core.pipeline.exceptions import SafelyIgnoreableError
from gazetrack_core.producer.interface import Producer


class EngineError(Exception):
    """Base exception for engine errors"""

    pass


class ValidationError(EngineError):
    """Raised when parameter validation fails"""

    pass


class CircuitBreakerError(EngineError):
    """Raised when circuit breaker is open"""

    pass


@dataclass
class CircuitBreakerState:
    failure_count: int = 0
    last_failure_time: float = 0.0
    is_open: bool = False


class Engine(AsyncContextManagerMixin):
    def __init__(
        self,
        fn: Pipeline,
        bus: EventBus,
        source_producers: Optional[list[Producer[np.ndarray]]] = None,
        gaze_producers: Optional[list[Producer[tuple[float, float]]]] = None,
        scene_producer: Optional[Producer[np.ndarray]] = None,
        max_failures: int = 5,
        recovery_timeout: float = 30.0,
        rate_limit: float = 0.01,  # Minimum time between iterations in seconds
    ):
        if not fn:
            raise ValidationError("Pipeline function cannot be None")
        if not bus:
            raise ValidationError("Event bus cannot be None")
        if max_failures <= 0:
            raise ValidationError("Max failures must be positive")
        if recovery_timeout <= 0:
            raise ValidationError("Recovery timeout must be positive")
        if rate_limit < 0:
            raise ValidationError("Rate limit cannot be negative")

        self._pp = source_producers
        self._gp = gaze_producers
        self._sp = scene_producer

        self._fn = fn
        self._bus = bus
        self._max_failures = max_failures
        self._recovery_timeout = recovery_timeout
        self._rate_limit = rate_limit

        self._running = threading.Event()
        self._circuit_breaker = CircuitBreakerState()
        self._last_iteration_time = 0.0

        self._lock: anyio.Lock | None = None
        self._state_lock: anyio.Lock | None = None

        self.context: asyncer.TaskGroup | None = None

    @asynccontextmanager
    async def __asynccontextmanager__(self) -> AsyncGenerator[Self]:
        self.context = asyncer.create_task_group()
        async with self.context:
            self._lock = anyio.Lock()
            self._state_lock = anyio.Lock()
            yield self

    @staticmethod
    def safe(method: Callable):
        async def wrapper(self, *args, **kwargs):
            # Use atomic check and set to prevent race condition
            async with self._state_lock:
                if self._running.is_set():
                    self._running.clear()
                    was_running = True
                else:
                    was_running = False

            try:
                async with self._lock:
                    await method(self, *args, **kwargs)
            finally:
                # Restore running state if it was previously running
                if was_running:
                    async with self._state_lock:
                        self._running.set()

        return wrapper

    @property
    def assembled(self) -> bool:
        return self._pp is not None and self._gp is not None and self._sp is not None

    @property
    def running(self) -> bool:
        return self._running.is_set() and self._lock is not None and self._lock.locked()

    @safe
    async def set_source_producers(self, source_producers: list[Producer[np.ndarray]]):
        self._pp = source_producers

    @safe
    async def set_gaze_producers(
        self, gaze_producers: list[Producer[tuple[float, float]]]
    ):
        self._gp = gaze_producers

    @safe
    async def set_scene_producer(self, scene_producer: Producer[np.ndarray]):
        self._sp = scene_producer

    @safe
    async def set_environment(
        self,
        source_producers: list[Producer[np.ndarray]],
        gaze_producers: list[Producer[tuple[float, float]]],
        scene_producer: Producer[np.ndarray],
    ):
        self._pp = source_producers
        self._gp = gaze_producers
        self._sp = scene_producer

    @safe
    async def set_pipeline(self, fn: Pipeline):
        self._fn = fn

    async def _ctx(self, stack: AsyncExitStack):
        for client in self._pp:
            await stack.enter_async_context(client)
            logger.info(f"{client} initialized")
        for client in self._gp:
            await stack.enter_async_context(client)
            logger.info(f"{client} initialized")
        await stack.enter_async_context(self._sp)
        logger.info(f"{self._sp} initialized")

    async def _check_circuit_breaker(self) -> bool:
        """Check if circuit breaker should prevent execution"""
        async with self._state_lock:
            current_time = time.time()

            if self._circuit_breaker.is_open:
                if (
                    current_time - self._circuit_breaker.last_failure_time
                    > self._recovery_timeout
                ):
                    # Attempt to close circuit breaker
                    self._circuit_breaker.is_open = False
                    self._circuit_breaker.failure_count = 0
                    logger.info("Circuit breaker closed - attempting recovery")
                    return True
                else:
                    return False
            return True

    async def _record_failure(self):
        """Record a failure and potentially open circuit breaker"""
        async with self._state_lock:
            self._circuit_breaker.failure_count += 1
            self._circuit_breaker.last_failure_time = time.time()

            if self._circuit_breaker.failure_count >= self._max_failures:
                self._circuit_breaker.is_open = True
                logger.warning(
                    f"Circuit breaker opened after {self._circuit_breaker.failure_count} failures"
                )

    async def _record_success(self):
        """Record a success and reset failure count"""
        async with self._state_lock:
            if self._circuit_breaker.failure_count > 0:
                self._circuit_breaker.failure_count = 0
                logger.debug("Circuit breaker failure count reset")

    async def _enforce_rate_limit(self):
        """Enforce minimum time between iterations"""
        current_time = time.time()
        time_since_last = current_time - self._last_iteration_time

        if time_since_last < self._rate_limit:
            sleep_time = self._rate_limit - time_since_last
            await anyio.sleep(sleep_time)

        self._last_iteration_time = time.time()

    async def _pass(self) -> None:
        try:
            # Check circuit breaker before processing
            if not await self._check_circuit_breaker():
                await self._bus.publish(
                    Event("error", "Circuit breaker is open - processing paused")
                )
                await anyio.sleep(1.0)  # Wait before retrying
                return

            # Enforce rate limiting
            await self._enforce_rate_limit()

            it = assemble_payload(self._pp, self._gp, self._sp)
            it = stamp(it)
            match await asyncer.asyncify(self._fn)(it):
                case Success(value):
                    await self._bus.publish(Event("result", value))
                    await self._record_success()
                case Failure(value):
                    match value:
                        case SafelyIgnoreableError():
                            logger.warning(f"Safe to ignore error: {value}")
                            await self._record_success()
                            return
                        case _:
                            error_msg = str(value)
                            await self._bus.publish(Event("error", error_msg))
                            await self._record_failure()
                            logger.error(f"Pipeline processing failed: {error_msg}")
        except RuntimeError as e:
            error_msg = str(e)
            await self._bus.publish(Event("error", error_msg))
            await self._record_failure()
            logger.error(f"Runtime error in engine: {error_msg}")
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            await self._bus.publish(Event("error", error_msg))
            await self._record_failure()
            logger.error(f"Unexpected error in engine: {error_msg}")
        finally:
            await anyio.sleep(0)

    async def _loop(self) -> None:
        async with self._lock:
            async with self._state_lock:
                self._running.set()

            async with AsyncExitStack() as stack:
                await self._ctx(stack)
                logger.info("Engine started")

                try:
                    while self._running.is_set():
                        await self._pass()
                except Exception as e:
                    logger.error(f"Engine loop error: {str(e)}")
                    await self._bus.publish(
                        Event("error", f"Engine loop error: {str(e)}")
                    )
                finally:
                    async with self._state_lock:
                        self._running.clear()
                    logger.info("Engine stopped")

    def halt(self):
        """Safely halt the engine"""
        self._running.clear()

        if (
            self.context is not None
            and hasattr(self.context, "cancel_scope")
            and self.context.cancel_scope
        ):
            self.context.cancel_scope.cancel()
        logger.info("Engine halt requested")

    def __call__(self, *args, **kwargs) -> bool:
        if self.running or not self.assembled:
            logger.warning(
                f"Engine start failed - running: {self.running}, assembled: {self.assembled}"
            )
            return False

        try:
            self.context.soonify(self._loop)()
            logger.info("Engine start initiated")
            return True
        except Exception as e:
            logger.error(f"Failed to start engine: {str(e)}")
            return False
