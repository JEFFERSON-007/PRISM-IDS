"""Master Hybrid Intrusion Detection Engine Lifecycle Controller."""

import asyncio
import time
from typing import Any, Dict, Optional
import structlog
from agent.core.config import agent_settings
from agent.detection.detection_fusion import DetectionFusion
from agent.detection.detection_queue import DetectionQueue
from agent.detection.detection_statistics import DetectionStatistics
from agent.detection.ml_engine import MLEngine
from agent.detection.signature_engine import SignatureEngine
from agent.feature_extraction.feature_models import FeatureVector
from agent.feature_extraction.feature_queue import FeatureQueue

logger = structlog.get_logger("prism_agent.hybrid_engine")


class HybridEngine:
    """High-level Hybrid Intrusion Detection Engine unifying Signature and ML detection."""

    def __init__(self, input_feature_queue: Optional[FeatureQueue] = None) -> None:
        self.input_feature_queue = input_feature_queue
        self.output_queue = DetectionQueue(maxsize=agent_settings.DETECTION_QUEUE_MAX_SIZE)
        self.signature_engine = SignatureEngine()
        self.ml_engine = MLEngine()
        self.statistics = DetectionStatistics()

        self._is_initialized: bool = False
        self._is_running: bool = False
        self._consumer_task: Optional[asyncio.Task] = None

    def bind_feature_queue(self, feature_queue: FeatureQueue) -> None:
        """Bind input FeatureQueue from Feature Extraction Engine."""
        self.input_feature_queue = feature_queue
        self._is_initialized = True

    async def start(self) -> None:
        """Start Hybrid Detection Engine consumer loop."""
        if not self.input_feature_queue:
            raise RuntimeError("Cannot start HybridEngine without a bound FeatureQueue")

        if self._is_running:
            logger.warning("HybridEngine is already running")
            return

        self._is_running = True
        self.statistics.start()
        self._consumer_task = asyncio.create_task(self._feature_consumer_loop())
        logger.info(
            "Hybrid Intrusion Detection Engine started successfully",
            signature_enabled=agent_settings.SIGNATURE_ENGINE_ENABLED,
            ml_enabled=agent_settings.ML_ENGINE_ENABLED,
            ml_available=self.ml_engine.is_available,
        )

    async def stop(self) -> None:
        """Stop Hybrid Detection Engine."""
        self._is_running = False
        if self._consumer_task:
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass
            self._consumer_task = None

        self.statistics.stop()
        logger.info("Hybrid Intrusion Detection Engine stopped")

    async def _feature_consumer_loop(self) -> None:
        """Continuous consumer popping FeatureVectors from input queue."""
        while self._is_running:
            try:
                vector: FeatureVector = await self.input_feature_queue.get()
                await self._evaluate_vector_async(vector)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self.statistics.record_error()
                logger.error("Error in hybrid detection consumer loop", error=str(exc))

    async def _evaluate_vector_async(self, vector: FeatureVector) -> None:
        """Evaluate vector across Signature & ML engines asynchronously, fusing results."""
        start_t = time.perf_counter()
        try:
            # 1. Signature Engine Evaluation
            matched_rules = []
            if agent_settings.SIGNATURE_ENGINE_ENABLED:
                matched_rules = self.signature_engine.evaluate(vector)

            # 2. Machine Learning Engine Evaluation (Async Offloaded to Thread Worker Pool)
            ml_result = None
            if agent_settings.ML_ENGINE_ENABLED and self.ml_engine.is_available:
                ml_result = await self.ml_engine.predict_async(vector)

            # 3. Detection Fusion
            detection = DetectionFusion.fuse(vector, matched_rules, ml_result)

            dur_ms = (time.perf_counter() - start_t) * 1000.0
            self.statistics.record_evaluation(dur_ms)

            if detection:
                if matched_rules:
                    self.statistics.record_signature_hit()
                if ml_result and ml_result.is_malicious:
                    self.statistics.record_ml_hit()

                pushed = self.output_queue.push_nowait(detection)
                if not pushed:
                    self.statistics.record_drop()
                    logger.warning("Detection queue full: dropped detection result")
        except Exception as exc:
            self.statistics.record_error()
            logger.error("Error evaluating feature vector", error=str(exc))

    def get_status(self) -> Dict[str, Any]:
        """Return runtime state and performance metrics summary."""
        return {
            "initialized": self._is_initialized,
            "running": self._is_running,
            "queue_size": self.output_queue.size,
            "signature_engine_ready": True,
            "ml_engine_ready": self.ml_engine.is_available,
            "statistics": self.statistics.get_summary(),
        }
