"""Bounded Output Flow Queue for Completed Flow Records."""

import asyncio
from typing import Optional
import structlog
from agent.core.config import agent_settings
from agent.flow.flow_models import Flow

logger = structlog.get_logger("prism_agent.flow_queue")


class FlowQueue:
    """Thread-safe output queue storing completed/expired Flow records for downstream processing."""

    def __init__(self, maxsize: Optional[int] = None) -> None:
        self.maxsize = maxsize or agent_settings.FLOW_QUEUE_MAX_SIZE
        self._queue: asyncio.Queue[Flow] = asyncio.Queue(maxsize=self.maxsize)
        self._dropped_count: int = 0
        self._processed_count: int = 0

    @property
    def size(self) -> int:
        """Current number of completed flows in queue."""
        return self._queue.qsize()

    @property
    def dropped_count(self) -> int:
        """Total expired flows dropped due to queue overflow."""
        return self._dropped_count

    @property
    def processed_count(self) -> int:
        """Total flows popped by consumers."""
        return self._processed_count

    def push_nowait(self, flow: Flow) -> bool:
        """Push completed flow into queue without blocking."""
        if self._queue.full():
            try:
                self._queue.get_nowait()
                self._dropped_count += 1
                logger.warning("Flow queue full: dropped oldest completed flow", dropped_total=self._dropped_count)
            except asyncio.QueueEmpty:
                pass

        try:
            self._queue.put_nowait(flow)
            return True
        except asyncio.QueueFull:
            self._dropped_count += 1
            return False

    async def get(self) -> Flow:
        """Pop next completed flow from queue."""
        flow = await self._queue.get()
        self._processed_count += 1
        self._queue.task_done()
        return flow

    def clear(self) -> None:
        """Clear output queue."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except asyncio.QueueEmpty:
                break
