"""Thread-Safe Bounded Packet Queue with Ring-Buffer Overflow Drop Protection."""

import asyncio
from collections import deque
import threading
from typing import Optional
import structlog
from agent.capture.packet_models import ParsedPacket
from agent.core.config import agent_settings

logger = structlog.get_logger("prism_agent.packet_queue")


class PacketQueue:
    """Thread-safe bounded queue for buffering captured ParsedPacket objects between OS sniffing thread and Asyncio loop."""

    def __init__(self, maxsize: Optional[int] = None) -> None:
        self.maxsize = maxsize or agent_settings.QUEUE_MAX_SIZE
        self._deque: deque[ParsedPacket] = deque(maxlen=self.maxsize)
        self._lock = threading.Lock()
        self._event = asyncio.Event()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._dropped_count: int = 0
        self._processed_count: int = 0

    @property
    def size(self) -> int:
        """Current number of queued packets."""
        with self._lock:
            return len(self._deque)

    @property
    def dropped_count(self) -> int:
        """Total packets dropped due to queue overflow."""
        with self._lock:
            return self._dropped_count

    @property
    def processed_count(self) -> int:
        """Total packets popped by consumers."""
        with self._lock:
            return self._processed_count

    def push_nowait(self, packet: ParsedPacket) -> bool:
        """Push packet into queue without blocking. Drop oldest packet if full."""
        with self._lock:
            if len(self._deque) >= self.maxsize:
                self._deque.popleft()  # Drop oldest packet (FIFO ring buffer)
                self._dropped_count += 1
                logger.warning("Packet queue full: dropped oldest packet", dropped_total=self._dropped_count)

            self._deque.append(packet)

            # Signal asyncio event loop thread-safely
            if self._loop and self._loop.is_running():
                self._loop.call_soon_threadsafe(self._event.set)
            else:
                self._event.set()
            return True

    async def get(self) -> ParsedPacket:
        """Pop next packet from queue asynchronously."""
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        while True:
            with self._lock:
                if self._deque:
                    packet = self._deque.popleft()
                    self._processed_count += 1
                    if not self._deque:
                        self._event.clear()
                    return packet

            # Wait for next packet push signal
            await self._event.wait()

    def clear(self) -> None:
        """Drain all queued items."""
        with self._lock:
            self._deque.clear()
            self._event.clear()
