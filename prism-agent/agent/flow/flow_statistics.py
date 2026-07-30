"""Flow Engine Live Metrics & Performance Statistics Monitor."""

import time
from typing import Any, Dict, Optional


class FlowStatistics:
    """Tracks active flow counts, creation/expiration rates, and packet processing volumes."""

    def __init__(self) -> None:
        self.start_time: Optional[float] = None
        self.stop_time: Optional[float] = None
        self.created_flows: int = 0
        self.completed_flows: int = 0
        self.expired_flows: int = 0
        self.packets_processed: int = 0
        self.bytes_processed: int = 0
        self.error_count: int = 0

    def start(self) -> None:
        """Start statistics monitor."""
        self.start_time = time.perf_counter()
        self.stop_time = None

    def stop(self) -> None:
        """Stop statistics monitor."""
        self.stop_time = time.perf_counter()

    def record_flow_created(self) -> None:
        """Increment created flows counter."""
        self.created_flows += 1

    def record_flow_expired(self) -> None:
        """Increment expired flows counter."""
        self.completed_flows += 1
        self.expired_flows += 1

    def record_packet(self, packet_bytes: int) -> None:
        """Increment packet & bytes processed counter."""
        self.packets_processed += 1
        self.bytes_processed += packet_bytes

    def record_error(self) -> None:
        """Increment error counter."""
        self.error_count += 1

    @property
    def duration_seconds(self) -> float:
        """Active monitoring duration in seconds."""
        if not self.start_time:
            return 0.0
        end = self.stop_time or time.perf_counter()
        return round(end - self.start_time, 2)

    @property
    def creation_rate(self) -> float:
        """Flow creation rate per second."""
        dur = self.duration_seconds
        if dur <= 0:
            return 0.0
        return round(self.created_flows / dur, 2)

    @property
    def expiration_rate(self) -> float:
        """Flow expiration rate per second."""
        dur = self.duration_seconds
        if dur <= 0:
            return 0.0
        return round(self.expired_flows / dur, 2)

    def get_summary(self, active_flow_count: int) -> Dict[str, Any]:
        """Return snapshot summary of metrics."""
        return {
            "active_flows": active_flow_count,
            "created_flows": self.created_flows,
            "completed_flows": self.completed_flows,
            "expired_flows": self.expired_flows,
            "packets_processed": self.packets_processed,
            "bytes_processed": self.bytes_processed,
            "creation_rate_fps": self.creation_rate,
            "expiration_rate_fps": self.expiration_rate,
            "duration_seconds": self.duration_seconds,
            "errors": self.error_count,
        }
