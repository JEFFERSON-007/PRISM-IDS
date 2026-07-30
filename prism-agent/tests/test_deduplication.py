"""Unit tests for AlertDeduplicator sliding window."""

from agent.detection.detection_models import DetectionMethodEnum, DetectionResult, RuleMatch, SeverityEnum
from agent.risk.deduplication import AlertDeduplicator


def test_alert_deduplication() -> None:
    """Test duplicate detection increments count instead of producing new alert."""
    dedup = AlertDeduplicator(dedup_window=60.0)

    rule = RuleMatch(rule_id="SIG-001", name="Port Scan", severity=SeverityEnum.HIGH, evidence={})
    det1 = DetectionResult(
        flow_id="f1",
        src_ip="192.168.1.10",
        dst_ip="10.0.0.1",
        src_port=100,
        dst_port=80,
        protocol="TCP",
        detection_method=DetectionMethodEnum.SIGNATURE,
        matched_rules=[rule],
        confidence_score=0.8,
        severity=SeverityEnum.HIGH,
    )

    is_new1, alert1 = dedup.process_detection(det1)
    assert is_new1 is True
    assert alert1.occurrence_count == 1

    # Second identical detection within window
    det2 = DetectionResult(
        flow_id="f2",
        src_ip="192.168.1.10",
        dst_ip="10.0.0.1",
        src_port=101,
        dst_port=80,
        protocol="TCP",
        detection_method=DetectionMethodEnum.SIGNATURE,
        matched_rules=[rule],
        confidence_score=0.8,
        severity=SeverityEnum.HIGH,
    )

    is_new2, alert2 = dedup.process_detection(det2)
    assert is_new2 is False
    assert alert2.occurrence_count == 2
    assert alert1.alert_id == alert2.alert_id
