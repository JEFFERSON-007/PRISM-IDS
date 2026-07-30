"""Unit tests for Alert models and schemas."""

from datetime import datetime, timezone
import uuid
from app.schemas.alert import AlertCreate, AlertRead


def test_alert_schema_validation() -> None:
    """Test validating AlertCreate schema."""
    now = datetime.now(timezone.utc)
    alert_in = AlertCreate(
        alert_id="ALT-100",
        timestamp=now,
        detection_id="det-1",
        flow_id="flow-1",
        src_ip="192.168.1.50",
        dst_ip="10.0.0.1",
        src_port=1234,
        dst_port=80,
        protocol="TCP",
        risk_score=85.0,
        severity="HIGH",
        detection_method="HYBRID",
        confidence=0.9,
    )

    assert alert_in.alert_id == "ALT-100"
    assert alert_in.severity == "HIGH"
    assert alert_in.risk_score == 85.0
