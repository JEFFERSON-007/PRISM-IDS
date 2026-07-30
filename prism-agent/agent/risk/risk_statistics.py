"""Live Metrics & Performance Statistics Monitor for Risk Engine."""

import time
from typing import Any, Dict, Optional
from agent.detection.detection_models import SeverityEnum


class RiskStatistics:
    """Tracks alert generation volume, deduplication counts, transmission success, and severity distribution."""

    def __init__(self) -> None:
        self.start_time: Optional[float] = None
        self.stop_time: Optional[float] = None
        self.detections_consumed: int = 0
        self.alerts_generated: int = 0
        self.duplicate_alerts: int = 0
        self.total_risk_score_sum: float = 0.0
        self.severity_distribution: Dict[str, int] = {
            SeverityEnum.LOW.value: 0,
            SeverityEnum.MEDIUM.value: 0,
            SeverityEnum.HIGH.value: 0,
            SeverityEnum.CRITICAL.value: 0,
        }
        self.error_count: int = 0

    def start(self) -> None:
        """Start statistics timer."""
        self.start_time = time.perf_counter()
        self.stop_time = None

    def stop(self) -> None:
        """Stop statistics timer."""
        self.stop_time = time.perf_counter()

    def record_detection_consumed(self) -> None:
        """Record consumed detection."""
        self.detections_consumed += 1

    def record_alert_generated(self, risk_score: float, severity: SeverityEnum) -> None:
        """Record newly generated alert."""
        self.alerts_generated += 1
        self.total_risk_score_sum += risk_score
        sev_key = severity.value
        self.severity_distribution[sev_key] = self.severity_distribution.get(sev_key, 0) + 1

    def record_duplicate_suppressed(self) -> None:
        """Record suppressed duplicate alert."""
        self.duplicate_alerts += 1

    def record_error(self) -> None:
        """Record exception."""
        self.error_count += 1

    @property
    def duration_seconds(self) -> float:
        """Active engine duration in seconds."""
        if not self.start_time:
            return 0.0
        end = self.stop_time or time.perf_counter()
        return round(end - self.start_time, 2)

    @property
    def average_risk_score(self) -> float:
        """Compute average risk score across generated alerts."""
        if self.alerts_generated <= 0:
            return 0.0
        return round(self.total_risk_score_sum / self.alerts_generated, 1)

    def get_summary(self, queue_size: int, sent_count: int, failed_count: int) -> Dict[str, Any]:
        """Return metric snapshot summary."""
        return {
            "detections_consumed": self.detections_consumed,
            "alerts_generated": self.alerts_generated,
            "duplicate_alerts_suppressed": self.duplicate_alerts,
            "alerts_sent": sent_count,
            "alerts_failed": failed_count,
            "queue_size": queue_size,
            "average_risk_score": self.average_risk_score,
            "severity_distribution": self.severity_distribution,
            "duration_seconds": self.duration_seconds,
            "errors": self.error_count,
        }
