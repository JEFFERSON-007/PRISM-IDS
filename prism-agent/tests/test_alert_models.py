"""Unit tests for Alert DTO data model."""

from datetime import datetime, timezone
from agent.detection.detection_models import DetectionMethodEnum, SeverityEnum
from agent.risk.alert_models import Alert, AlertStatusEnum


def test_alert_instantiation_and_dict() -> None:
    """Test instantiating Alert DTO and calling to_dict()."""
    alert = Alert(
        detection_id="det-123",
        agent_id="agent-01",
        flow_id="f-456",
        src_ip="192.168.1.50",
        dst_ip="10.0.0.1",
        src_port=1234,
        dst_port=22,
        protocol="TCP",
        risk_score=85.5,
        severity=SeverityEnum.HIGH,
        detection_method=DetectionMethodEnum.HYBRID,
        confidence=0.9,
    )

    assert alert.status == AlertStatusEnum.OPEN
    assert alert.occurrence_count == 1
    assert alert.dst_port == 22

    d = alert.to_dict()
    assert d["agent_id"] == "agent-01"
    assert d["risk_score"] == 85.5
    assert d["severity"] == "HIGH"
