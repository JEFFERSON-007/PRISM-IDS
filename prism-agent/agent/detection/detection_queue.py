"""Bounded Output Queue storing unified DetectionResult records."""

import asyncio
from typing import Optional
import structlog
from agent.core.config import agent_settings
from agent.detection.detection_models import DetectionResult

logger = structlog.get_logger("prism_agent.detection_queue")


class DetectionQueue:
    """Thread-safe output queue buffering DetectionResult objects for the downstream Risk Engine."""

    def __init__(self, maxsize: Optional[int] = None) -> None:
        self.maxsize = maxsize or agent_settings.DETECTION_QUEUE_MAX_SIZE
        self._queue: asyncio.Queue[DetectionResult] = asyncio.Queue(maxsize=self.maxsize)
        self._dropped_count: int = 0
        self._processed_count: int = 0

    @property
    def size(self) -> int:
        """Current number of queued DetectionResults."""
        return self._queue.qsize()

    @property
    def dropped_count(self) -> int:
        """Total detections dropped due to queue overflow."""
        return self._dropped_count

    @property
    def processed_count(self) -> int:
        """Total detections popped by consumers."""
        return self._processed_count

    def push_nowait(self, detection: DetectionResult) -> bool:
        """Push DetectionResult into queue without blocking."""
        if self._queue.full():
            try:
                self._queue.get_nowait()
                self._dropped_count += 1
                logger.warning("Detection queue full: dropped oldest detection result", dropped_total=self._dropped_count)
            except asyncio.QueueEmpty:
                pass

        try:
            self._queue.put_nowait(detection)
            return True
        except asyncio.QueueFull:
            self._dropped_count += 1
            return False

    async def get(self) -> DetectionResult:
        """Pop next DetectionResult from queue."""
        detection = await self._queue.get()
        self._processed_count += 1
        self._queue.task_done()
        return detection

    def clear(self) -> None:
        """Clear detection queue."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except asyncio.QueueEmpty:
                break
