"""Bounded Async Packet Queue with Backpressure and Overflow Drop Protection."""

import asyncio
from typing import Optional
import structlog
from agent.capture.packet_models import ParsedPacket
from agent.core.config import agent_settings

logger = structlog.get_logger("prism_agent.packet_queue")


class PacketQueue:
    """Thread-safe bounded queue for buffering captured ParsedPacket objects."""

    def __init__(self, maxsize: Optional[int] = None) -> None:
        self.maxsize = maxsize or agent_settings.QUEUE_MAX_SIZE
        self._queue: asyncio.Queue[ParsedPacket] = asyncio.Queue(maxsize=self.maxsize)
        self._dropped_count: int = 0
        self._processed_count: int = 0

    @property
    def size(self) -> int:
        """Current number of queued packets."""
        return self._queue.qsize()

    @property
    def dropped_count(self) -> int:
        """Total packets dropped due to queue overflow."""
        return self._dropped_count

    @property
    def processed_count(self) -> int:
        """Total packets popped by consumers."""
        return self._processed_count

    def push_nowait(self, packet: ParsedPacket) -> bool:
        """Push packet into queue without blocking. Drop oldest packet if full."""
        if self._queue.full():
            try:
                # Discard oldest packet to make room (FIFO ring-buffer behavior)
                self._queue.get_nowait()
                self._dropped_count += 1
                logger.warning("Packet queue full: dropped oldest packet", dropped_total=self._dropped_count)
            except asyncio.QueueEmpty:
                pass

        try:
            self._queue.put_nowait(packet)
            return True
        except asyncio.QueueFull:
            self._dropped_count += 1
            return False

    async def get(self) -> ParsedPacket:
        """Pop next packet from queue."""
        packet = await self._queue.get()
        self._processed_count += 1
        self._queue.task_done()
        return packet

    def clear(self) -> None:
        """Drain all queued items."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except asyncio.QueueEmpty:
                break
