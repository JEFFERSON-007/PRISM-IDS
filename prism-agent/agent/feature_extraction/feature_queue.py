"""Bounded Output Queue storing validated FeatureVector records."""

import asyncio
from typing import Optional
import structlog
from agent.core.config import agent_settings
from agent.feature_extraction.feature_models import FeatureVector

logger = structlog.get_logger("prism_agent.feature_queue")


class FeatureQueue:
    """Thread-safe output queue storing validated FeatureVectors for downstream detection engines."""

    def __init__(self, maxsize: Optional[int] = None) -> None:
        self.maxsize = maxsize or agent_settings.FEATURE_QUEUE_MAX_SIZE
        self._queue: asyncio.Queue[FeatureVector] = asyncio.Queue(maxsize=self.maxsize)
        self._dropped_count: int = 0
        self._processed_count: int = 0

    @property
    def size(self) -> int:
        """Current number of queued FeatureVectors."""
        return self._queue.qsize()

    @property
    def dropped_count(self) -> int:
        """Total vectors dropped due to queue overflow."""
        return self._dropped_count

    @property
    def processed_count(self) -> int:
        """Total vectors popped by consumers."""
        return self._processed_count

    def push_nowait(self, vector: FeatureVector) -> bool:
        """Push FeatureVector into queue without blocking."""
        if self._queue.full():
            try:
                self._queue.get_nowait()
                self._dropped_count += 1
                logger.warning("Feature queue full: dropped oldest feature vector", dropped_total=self._dropped_count)
            except asyncio.QueueEmpty:
                pass

        try:
            self._queue.put_nowait(vector)
            return True
        except asyncio.QueueFull:
            self._dropped_count += 1
            return False

    async def get(self) -> FeatureVector:
        """Pop next FeatureVector from queue."""
        vector = await self._queue.get()
        self._processed_count += 1
        self._queue.task_done()
        return vector

    def clear(self) -> None:
        """Clear feature queue."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except asyncio.QueueEmpty:
                break
