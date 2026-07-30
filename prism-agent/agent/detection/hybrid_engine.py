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
                self._evaluate_vector(vector)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self.statistics.record_error()
                logger.error("Error in hybrid detection consumer loop", error=str(exc))

    def _evaluate_vector(self, vector: FeatureVector) -> None:
        """Evaluate vector across Signature & ML engines, fusing results."""
        start_t = time.perf_counter()
        try:
            # 1. Signature Engine Evaluation
            matched_rules = []
            if agent_settings.SIGNATURE_ENGINE_ENABLED:
                matched_rules = self.signature_engine.evaluate(vector)

            # 2. Machine Learning Engine Evaluation
            ml_result = None
            if agent_settings.ML_ENGINE_ENABLED and self.ml_engine.is_available:
                ml_result = self.ml_engine.predict(vector)

            # 3. Detection Fusion
            detection = DetectionFusion.fuse(vector, matched_rules, ml_result)

            dur_ms = (time.perf_counter() - start_t) * 1000.0
            self.statistics.record_processed(dur_ms)

            if detection and detection.confidence_score >= agent_settings.CONFIDENCE_THRESHOLD:
                is_ml_pos = ml_result.is_malicious if ml_result else False
                self.output_queue.push_nowait(detection)
                self.statistics.record_detection(len(matched_rules), is_ml_pos)
                logger.info(
                    "Detection output queued",
                    detection_id=detection.detection_id,
                    method=detection.detection_method.value,
                    severity=detection.severity.value,
                    confidence=detection.confidence_score,
                )
        except Exception as exc:
            self.statistics.record_error()
            logger.error("Failed to evaluate feature vector in HybridEngine", flow_id=vector.flow_id, error=str(exc))

    def get_status(self) -> Dict[str, Any]:
        """Return runtime state and detection statistics."""
        return {
            "initialized": self._is_initialized,
            "running": self._is_running,
            "ml_model_loaded": self.ml_engine.is_available,
            "signature_rules_count": len(self.signature_engine.rules),
            "statistics": self.statistics.get_summary(self.output_queue.size),
        }
