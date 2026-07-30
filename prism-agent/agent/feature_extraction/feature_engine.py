"""Master Feature Extraction Engine Lifecycle Controller."""

import asyncio
import time
from typing import Any, Dict, Optional
import structlog
from agent.core.config import agent_settings
from agent.feature_extraction.feature_pipeline import FeaturePipeline
from agent.feature_extraction.feature_queue import FeatureQueue
from agent.feature_extraction.feature_statistics import FeatureStatistics
from agent.feature_extraction.feature_validator import FeatureValidator
from agent.flow.flow_models import Flow
from agent.flow.flow_queue import FlowQueue

logger = structlog.get_logger("prism_agent.feature_engine")


class FeatureEngine:
    """High-level Feature Extraction Engine consuming expired flows and outputting FeatureVectors."""

    def __init__(self, input_flow_queue: Optional[FlowQueue] = None) -> None:
        self.input_flow_queue = input_flow_queue
        self.output_queue = FeatureQueue(maxsize=agent_settings.FEATURE_QUEUE_MAX_SIZE)
        self.statistics = FeatureStatistics()

        self._is_initialized: bool = False
        self._is_running: bool = False
        self._consumer_task: Optional[asyncio.Task] = None

    def bind_flow_queue(self, flow_queue: FlowQueue) -> None:
        """Bind input FlowQueue from Flow Engine."""
        self.input_flow_queue = flow_queue
        self._is_initialized = True

    async def start(self) -> None:
        """Start Feature Extraction Engine consumer loop."""
        if not self.input_flow_queue:
            raise RuntimeError("Cannot start FeatureEngine without a bound FlowQueue")

        if self._is_running:
            logger.warning("FeatureEngine is already running")
            return

        self._is_running = True
        self.statistics.start()
        self._consumer_task = asyncio.create_task(self._flow_consumer_loop())
        logger.info("Feature Extraction Engine started successfully")

    async def stop(self) -> None:
        """Stop Feature Extraction Engine."""
        self._is_running = False
        if self._consumer_task:
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass
            self._consumer_task = None

        self.statistics.stop()
        logger.info("Feature Extraction Engine stopped")

    async def _flow_consumer_loop(self) -> None:
        """Continuous consumer popping completed Flow objects from input queue."""
        while self._is_running:
            try:
                flow: Flow = await self.input_flow_queue.get()
                self._process_flow(flow)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self.statistics.record_error()
                logger.error("Error in feature extraction flow consumer", error=str(exc))

    def _process_flow(self, flow: Flow) -> None:
        """Extract and validate feature vector for flow."""
        start_t = time.perf_counter()
        try:
            vector = FeaturePipeline.extract_features(flow)
            is_valid, sanitized_vector, reason = FeatureValidator.validate_and_sanitize(
                vector, strict=agent_settings.FEATURE_VALIDATION_STRICT
            )

            dur_ms = (time.perf_counter() - start_t) * 1000.0

            if is_valid:
                self.output_queue.push_nowait(sanitized_vector)
                self.statistics.record_generated(dur_ms)
                logger.debug(
                    "Extracted FeatureVector",
                    flow_id=flow.flow_id,
                    protocol=flow.protocol,
                    duration_ms=round(dur_ms, 2),
                )
            else:
                self.statistics.record_rejected()
                logger.warning("Rejected invalid FeatureVector", flow_id=flow.flow_id, reason=reason)
        except Exception as exc:
            self.statistics.record_error()
            logger.error("Failed to extract features for flow", flow_id=flow.flow_id, error=str(exc))

    def get_status(self) -> Dict[str, Any]:
        """Return engine runtime state and performance metrics."""
        return {
            "initialized": self._is_initialized,
            "running": self._is_running,
            "statistics": self.statistics.get_summary(self.output_queue.size),
        }
