"""Background Alert Transmission Worker with Exponential Backoff Retries."""

import asyncio
from typing import Optional
import structlog
from agent.communication.http_client import AgentHTTPClient
from agent.core.config import agent_settings
from agent.risk.alert_models import Alert
from agent.risk.alert_queue import AlertQueue

logger = structlog.get_logger("prism_agent.alert_sender")


class AlertSender:
    """Delivers alerts securely to PRISM Server over HTTP with retry resilience."""

    def __init__(self, queue: AlertQueue, http_client: AgentHTTPClient) -> None:
        self.queue = queue
        self.http_client = http_client
        self.max_retries = agent_settings.ALERT_MAX_RETRIES
        self.base_backoff = agent_settings.ALERT_RETRY_BACKOFF

        self._running: bool = False
        self._task: Optional[asyncio.Task] = None
        self._sent_count: int = 0
        self._failed_count: int = 0

    @property
    def sent_count(self) -> int:
        """Total alerts successfully sent to PRISM Server."""
        return self._sent_count

    @property
    def failed_count(self) -> int:
        """Total alerts failed after max retries."""
        return self._failed_count

    async def start(self) -> None:
        """Start background alert transmission loop."""
        self._running = True
        self._task = asyncio.create_task(self._send_loop())
        logger.info("Alert transmission worker started")

    async def stop(self) -> None:
        """Stop background transmission worker."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Alert transmission worker stopped")

    async def _send_loop(self) -> None:
        """Continuous consumer loop sending alerts to PRISM Server."""
        while self._running:
            try:
                alert: Alert = await self.queue.get()
                success = await self._send_alert_with_retry(alert)
                if success:
                    self._sent_count += 1
                else:
                    self._failed_count += 1
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Error in alert transmission loop", error=str(exc))

    async def _send_alert_with_retry(self, alert: Alert) -> bool:
        """Post alert payload with exponential backoff retries."""
        payload = alert.to_dict()

        for attempt in range(1, self.max_retries + 1):
            try:
                response = await self.http_client.post("/api/v1/alerts", json_data=payload)
                logger.info(
                    "Alert transmitted successfully to PRISM Server",
                    alert_id=alert.alert_id,
                    severity=alert.severity.value,
                    attempt=attempt,
                )
                return True
            except Exception as exc:
                backoff = self.base_backoff * (2 ** (attempt - 1))
                logger.warning(
                    "Alert transmission attempt failed; retrying...",
                    alert_id=alert.alert_id,
                    attempt=attempt,
                    max_retries=self.max_retries,
                    backoff_sec=backoff,
                    error=str(exc),
                )
                if attempt < self.max_retries:
                    try:
                        await asyncio.sleep(backoff)
                    except asyncio.CancelledError:
                        break

        logger.error("Failed to deliver alert to PRISM Server after maximum retries", alert_id=alert.alert_id)
        return False
