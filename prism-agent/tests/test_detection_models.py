"""Unit tests for Detection Data Models."""

from datetime import datetime, timezone
from agent.detection.detection_models import (
    DetectionMethodEnum,
    DetectionResult,
    MLPredictionResult,
    RuleMatch,
    SeverityEnum,
)


def test_detection_result_instantiation() -> None:
    """Test creating unified DetectionResult DTO."""
    result = DetectionResult(
        flow_id="f-123",
        src_ip="192.168.1.100",
        dst_ip="10.0.0.1",
        src_port=12345,
        dst_port=80,
        protocol="TCP",
        detection_method=DetectionMethodEnum.HYBRID,
        matched_rules=[
            RuleMatch(
                rule_id="SIG-001",
                name="Port Scanning Activity Detected",
                severity=SeverityEnum.HIGH,
                evidence={"packets": 50},
            )
        ],
        ml_prediction=MLPredictionResult(
            is_malicious=True,
            probability=0.92,
            model_name="RandomForest",
            confidence=0.92,
        ),
        confidence_score=0.95,
        severity=SeverityEnum.CRITICAL,
        evidence={"traffic": "suspicious"},
    )

    assert result.detection_method == DetectionMethodEnum.HYBRID
    assert result.severity == SeverityEnum.CRITICAL
    assert result.confidence_score == 0.95
    assert len(result.matched_rules) == 1
