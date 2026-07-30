"""Unit tests for RiskCalculator algorithm."""

from agent.detection.detection_models import DetectionMethodEnum, DetectionResult, SeverityEnum
from agent.risk.risk_calculator import RiskCalculator


def test_calculate_risk_critical() -> None:
    """Test risk calculation for critical detection targeting SSH port 22."""
    detection = DetectionResult(
        flow_id="f-crit",
        src_ip="1.1.1.1",
        dst_ip="2.2.2.2",
        src_port=1000,
        dst_port=22,  # SSH port bonus
        protocol="TCP",
        detection_method=DetectionMethodEnum.HYBRID,
        confidence_score=0.9,
        severity=SeverityEnum.CRITICAL,
    )

    risk = RiskCalculator.calculate_risk(detection, occurrence_count=1)
    assert 90.0 <= risk <= 100.0


def test_calculate_risk_frequency_multiplier() -> None:
    """Test repeat occurrences boost risk score."""
    detection = DetectionResult(
        flow_id="f-rep",
        src_ip="1.1.1.1",
        dst_ip="2.2.2.2",
        src_port=1000,
        dst_port=80,
        protocol="TCP",
        detection_method=DetectionMethodEnum.SIGNATURE,
        confidence_score=0.7,
        severity=SeverityEnum.MEDIUM,
    )

    risk1 = RiskCalculator.calculate_risk(detection, occurrence_count=1)
    risk10 = RiskCalculator.calculate_risk(detection, occurrence_count=10)
    assert risk10 > risk1
