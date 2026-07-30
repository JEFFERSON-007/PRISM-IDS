"""Live Performance Metrics & Detection Statistics Monitor."""

import time
from typing import Any, Dict, Optional


class DetectionStatistics:
    """Tracks feature vector processing volume, detection rate, and module match counters."""

    def __init__(self) -> None:
        self.start_time: Optional[float] = None
        self.stop_time: Optional[float] = None
        self.vectors_processed: int = 0
        self.detections_generated: int = 0
        self.rule_matches_count: int = 0
        self.ml_positives_count: int = 0
        self.total_processing_time_ms: float = 0.0
        self.error_count: int = 0

    def start(self) -> None:
        """Start statistics monitor."""
        self.start_time = time.perf_counter()
        self.stop_time = None

    def stop(self) -> None:
        """Stop statistics monitor."""
        self.stop_time = time.perf_counter()

    def record_processed(self, duration_ms: float) -> None:
        """Record a processed feature vector."""
        self.vectors_processed += 1
        self.total_processing_time_ms += duration_ms

    def record_detection(self, rule_count: int, is_ml_positive: bool) -> None:
        """Record a generated detection result."""
        self.detections_generated += 1
        self.rule_matches_count += rule_count
        if is_ml_positive:
            self.ml_positives_count += 1

    def record_error(self) -> None:
        """Record an exception."""
        self.error_count += 1

    @property
    def duration_seconds(self) -> float:
        """Active engine duration in seconds."""
        if not self.start_time:
            return 0.0
        end = self.stop_time or time.perf_counter()
        return round(end - self.start_time, 2)

    @property
    def processing_rate_vps(self) -> float:
        """Feature vectors processed per second."""
        dur = self.duration_seconds
        if dur <= 0:
            return 0.0
        return round(self.vectors_processed / dur, 2)

    @property
    def avg_processing_time_ms(self) -> float:
        """Average processing latency per vector in milliseconds."""
        if self.vectors_processed <= 0:
            return 0.0
        return round(self.total_processing_time_ms / self.vectors_processed, 3)

    def get_summary(self, queue_size: int) -> Dict[str, Any]:
        """Return metric snapshot summary."""
        return {
            "vectors_processed": self.vectors_processed,
            "detections_generated": self.detections_generated,
            "rule_matches_count": self.rule_matches_count,
            "ml_positives_count": self.ml_positives_count,
            "processing_rate_vps": self.processing_rate_vps,
            "avg_processing_time_ms": self.avg_processing_time_ms,
            "queue_size": queue_size,
            "duration_seconds": self.duration_seconds,
            "errors": self.error_count,
        }
