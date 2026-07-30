"""Master Risk Engine & Alert Management System Lifecycle Controller."""

import asyncio
from typing import Any, Dict, Optional
import structlog
from agent.communication.http_client import AgentHTTPClient
from agent.core.config import agent_settings
from agent.detection.detection_models import DetectionResult
from agent.detection.detection_queue import DetectionQueue
from agent.risk.alert_builder import AlertBuilder
from agent.risk.alert_queue import AlertQueue
from agent.risk.alert_sender import AlertSender
from agent.risk.risk_statistics import RiskStatistics

logger = structlog.get_logger("prism_agent.risk_engine")


class RiskEngine:
    """High-level Risk Engine coordinating risk scoring, deduplication, correlation, and alert transmission."""

    def __init__(self, input_detection_queue: Optional[DetectionQueue] = None, http_client: Optional[AgentHTTPClient] = None) -> None:
        self.input_detection_queue = input_detection_queue
        self.http_client = http_client or AgentHTTPClient()
        self.output_queue = AlertQueue(maxsize=agent_settings.ALERT_QUEUE_MAX_SIZE)
        self.builder = AlertBuilder()
        self.sender = AlertSender(queue=self.output_queue, http_client=self.http_client)
        self.statistics = RiskStatistics()

        self._is_initialized: bool = False
        self._is_running: bool = False
        self._consumer_task: Optional[asyncio.Task] = None

    def bind_detection_queue(self, detection_queue: DetectionQueue) -> None:
        """Bind input DetectionQueue from Hybrid Detection Engine."""
        self.input_detection_queue = detection_queue
        self._is_initialized = True

    def set_http_client(self, http_client: AgentHTTPClient) -> None:
        """Bind HTTP client for server transmission."""
        self.http_client = http_client
        self.sender.http_client = http_client

    async def start(self) -> None:
        """Start Risk Engine consumer and alert sender tasks."""
        if not self.input_detection_queue:
            raise RuntimeError("Cannot start RiskEngine without a bound DetectionQueue")

        if self._is_running:
            logger.warning("RiskEngine is already running")
            return

        self._is_running = True
        self.statistics.start()
        await self.sender.start()
        self._consumer_task = asyncio.create_task(self._detection_consumer_loop())
        logger.info("Risk Engine and Alert Management System started successfully")

    async def stop(self) -> None:
        """Stop Risk Engine and transmission worker."""
        self._is_running = False
        if self._consumer_task:
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass
            self._consumer_task = None

        await self.sender.stop()
        self.statistics.stop()
        logger.info("Risk Engine and Alert Management System stopped")

    async def _detection_consumer_loop(self) -> None:
        """Continuous consumer loop popping DetectionResult objects from input queue."""
        while self._is_running:
            try:
                detection: DetectionResult = await self.input_detection_queue.get()
                self._process_detection(detection)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self.statistics.record_error()
                logger.error("Error in risk engine detection consumer loop", error=str(exc))

    def _process_detection(self, detection: DetectionResult) -> None:
        """Process detection through risk calculation, deduplication, correlation, and queueing."""
        try:
            self.statistics.record_detection_consumed()
            is_new_alert, alert = self.builder.build_alert(detection)

            if is_new_alert:
                self.output_queue.push_nowait(alert)
                self.statistics.record_alert_generated(alert.risk_score, alert.severity)
                logger.info(
                    "New Security Alert generated",
                    alert_id=alert.alert_id,
                    severity=alert.severity.value,
                    risk_score=alert.risk_score,
                    flow_id=alert.flow_id,
                )
            else:
                self.statistics.record_duplicate_suppressed()
        except Exception as exc:
            self.statistics.record_error()
            logger.error("Failed to process detection in RiskEngine", flow_id=detection.flow_id, error=str(exc))

    def get_status(self) -> Dict[str, Any]:
        """Return engine runtime state and metrics summary."""
        return {
            "initialized": self._is_initialized,
            "running": self._is_running,
            "statistics": self.statistics.get_summary(
                queue_size=self.output_queue.size,
                sent_count=self.sender.sent_count,
                failed_count=self.sender.failed_count,
            ),
        }
