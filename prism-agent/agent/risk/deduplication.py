"""Sliding Window Alert Deduplication Service."""

from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
import structlog
from agent.core.config import agent_settings
from agent.detection.detection_models import DetectionResult
from agent.risk.alert_models import Alert
from agent.risk.risk_calculator import RiskCalculator
from agent.risk.severity_mapper import SeverityMapper

logger = structlog.get_logger("prism_agent.deduplication")


class AlertDeduplicator:
    """Prevents duplicate alert generation within a sliding time window."""

    def __init__(self, dedup_window: Optional[float] = None) -> None:
        self.dedup_window = dedup_window or agent_settings.ALERT_DEDUP_WINDOW
        # Key: (src_ip, dst_ip, dst_port, protocol, rule_id) -> Alert
        self._cache: Dict[Tuple[str, str, int, str, str], Alert] = {}

    def process_detection(self, detection: DetectionResult) -> Tuple[bool, Alert]:
        """Check if detection is a duplicate. Returns (is_new_alert, alert)."""
        now = datetime.now(timezone.utc)
        rule_key = detection.matched_rules[0].rule_id if detection.matched_rules else "ML"
        cache_key = (
            detection.src_ip,
            detection.dst_ip,
            detection.dst_port,
            detection.protocol,
            rule_key,
        )

        # Check if existing alert in cache is still within sliding window
        if cache_key in self._cache:
            existing_alert = self._cache[cache_key]
            elapsed_sec = (now - existing_alert.last_seen).total_seconds()

            if elapsed_sec <= self.dedup_window:
                # Update existing alert in-place
                existing_alert.occurrence_count += 1
                existing_alert.last_seen = now

                # Recalculate risk and severity with updated frequency
                new_risk = RiskCalculator.calculate_risk(detection, occurrence_count=existing_alert.occurrence_count)
                existing_alert.risk_score = new_risk
                existing_alert.severity = SeverityMapper.map_severity(new_risk)

                logger.info(
                    "Deduplicated repeated security alert",
                    alert_id=existing_alert.alert_id,
                    occurrence_count=existing_alert.occurrence_count,
                    updated_risk=new_risk,
                )
                return False, existing_alert

        # Instantiate new Alert DTO if not cached or window expired
        initial_risk = RiskCalculator.calculate_risk(detection, occurrence_count=1)
        severity = SeverityMapper.map_severity(initial_risk)

        new_alert = Alert(
            detection_id=detection.detection_id,
            agent_id="AGENT-LOCAL",  # Resolved dynamically by lifecycle
            flow_id=detection.flow_id,
            src_ip=detection.src_ip,
            dst_ip=detection.dst_ip,
            src_port=detection.src_port,
            dst_port=detection.dst_port,
            protocol=detection.protocol,
            risk_score=initial_risk,
            severity=severity,
            detection_method=detection.detection_method,
            matched_rules=detection.matched_rules,
            ml_prediction=detection.ml_prediction,
            confidence=detection.confidence_score,
            evidence_summary=detection.evidence,
        )

        self._cache[cache_key] = new_alert
        return True, new_alert

    def sweep_expired_cache(self) -> None:
        """Evict stale cache entries older than window."""
        now = datetime.now(timezone.utc)
        expired_keys = [
            k for k, alert in self._cache.items()
            if (now - alert.last_seen).total_seconds() > self.dedup_window
        ]
        for k in expired_keys:
            del self._cache[k]
