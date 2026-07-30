"""Bounded Outbound Alert Queue with Local Resilience."""

import asyncio
from typing import Optional
import structlog
from agent.core.config import agent_settings
from agent.risk.alert_models import Alert

logger = structlog.get_logger("prism_agent.alert_queue")


class AlertQueue:
    """Thread-safe bounded queue buffering Alert objects for server transmission."""

    def __init__(self, maxsize: Optional[int] = None) -> None:
        self.maxsize = maxsize or agent_settings.ALERT_QUEUE_MAX_SIZE
        self._queue: asyncio.Queue[Alert] = asyncio.Queue(maxsize=self.maxsize)
        self._dropped_count: int = 0
        self._processed_count: int = 0

    @property
    def size(self) -> int:
        """Current number of queued Alert objects."""
        return self._queue.qsize()

    @property
    def dropped_count(self) -> int:
        """Total alerts dropped due to queue overflow."""
        return self._dropped_count

    @property
    def processed_count(self) -> int:
        """Total alerts popped for transmission."""
        return self._processed_count

    def push_nowait(self, alert: Alert) -> bool:
        """Push Alert into queue without blocking."""
        if self._queue.full():
            try:
                self._queue.get_nowait()
                self._dropped_count += 1
                logger.warning("Alert queue full: dropped oldest alert record", dropped_total=self._dropped_count)
            except asyncio.QueueEmpty:
                pass

        try:
            self._queue.put_nowait(alert)
            return True
        except asyncio.QueueFull:
            self._dropped_count += 1
            return False

    async def get(self) -> Alert:
        """Pop next Alert from queue."""
        alert = await self._queue.get()
        self._processed_count += 1
        self._queue.task_done()
        return alert

    def clear(self) -> None:
        """Clear queue."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except asyncio.QueueEmpty:
                break
