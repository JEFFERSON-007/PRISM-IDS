"""Live Packet Capture Performance Statistics Monitor."""

from datetime import datetime, timezone
import time
from typing import Any, Dict, Optional


class CaptureStatistics:
    """Tracks live packet metrics, throughput, drops, and execution duration."""

    def __init__(self) -> None:
        self.start_time: Optional[float] = None
        self.stop_time: Optional[float] = None
        self.packets_captured: int = 0
        self.packets_dropped: int = 0
        self.packets_processed: int = 0
        self.bytes_captured: int = 0
        self.error_count: int = 0

    def start(self) -> None:
        """Start or reset statistics timer."""
        self.start_time = time.perf_counter()
        self.stop_time = None

    def stop(self) -> None:
        """Freeze statistics timer."""
        self.stop_time = time.perf_counter()

    def record_packet(self, packet_bytes: int) -> None:
        """Record a captured packet."""
        self.packets_captured += 1
        self.bytes_captured += packet_bytes

    def record_drop(self) -> None:
        """Record a dropped packet."""
        self.packets_dropped += 1

    def record_processed(self) -> None:
        """Record a processed packet."""
        self.packets_processed += 1

    def record_error(self) -> None:
        """Record a capture/parsing error."""
        self.error_count += 1

    @property
    def duration_seconds(self) -> float:
        """Calculate active capture duration in seconds."""
        if not self.start_time:
            return 0.0
        end = self.stop_time or time.perf_counter()
        return round(end - self.start_time, 2)

    @property
    def packets_per_second(self) -> float:
        """Compute average packets captured per second."""
        dur = self.duration_seconds
        if dur <= 0:
            return 0.0
        return round(self.packets_captured / dur, 2)

    def get_summary((self)) -> Dict[str, Any]:
        """Return snapshot summary of metrics."""
        return {
            "packets_captured": self.packets_captured,
            "packets_dropped": self.packets_dropped,
            "packets_processed": self.packets_processed,
            "bytes_captured": self.bytes_captured,
            "packets_per_second": self.packets_per_second,
            "duration_seconds": self.duration_seconds,
            "errors": self.error_count,
        }
