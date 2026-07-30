"""Live Performance Statistics for Feature Extraction Engine."""

import time
from typing import Any, Dict, Optional


class FeatureStatistics:
    """Tracks feature vector extraction volume, throughput, and error metrics."""

    def __init__(self) -> None:
        self.start_time: Optional[float] = None
        self.stop_time: Optional[float] = None
        self.vectors_generated: int = 0
        self.vectors_rejected: int = 0
        self.total_extraction_time_ms: float = 0.0
        self.error_count: int = 0

    def start(self) -> None:
        """Start statistics timer."""
        self.start_time = time.perf_counter()
        self.stop_time = None

    def stop(self) -> None:
        """Stop statistics timer."""
        self.stop_time = time.perf_counter()

    def record_generated(self, duration_ms: float) -> None:
        """Record a successfully extracted vector."""
        self.vectors_generated += 1
        self.total_extraction_time_ms += duration_ms

    def record_rejected(self) -> None:
        """Record a rejected invalid vector."""
        self.vectors_rejected += 1

    def record_error(self) -> None:
        """Record an extraction exception."""
        self.error_count += 1

    @property
    def duration_seconds(self) -> float:
        """Active engine duration in seconds."""
        if not self.start_time:
            return 0.0
        end = self.stop_time or time.perf_counter()
        return round(end - self.start_time, 2)

    @property
    def extraction_rate_vps(self) -> float:
        """Vectors generated per second."""
        dur = self.duration_seconds
        if dur <= 0:
            return 0.0
        return round(self.vectors_generated / dur, 2)

    @property
    def avg_extraction_time_ms(self) -> float:
        """Average extraction latency in milliseconds."""
        if self.vectors_generated <= 0:
            return 0.0
        return round(self.total_extraction_time_ms / self.vectors_generated, 3)

    def get_summary(self, queue_size: int) -> Dict[str, Any]:
        """Return metric snapshot."""
        return {
            "vectors_generated": self.vectors_generated,
            "vectors_rejected": self.vectors_rejected,
            "extraction_rate_vps": self.extraction_rate_vps,
            "avg_extraction_time_ms": self.avg_extraction_time_ms,
            "queue_size": queue_size,
            "duration_seconds": self.duration_seconds,
            "errors": self.error_count,
        }
