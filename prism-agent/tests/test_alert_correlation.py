"""Unit tests for AlertCorrelator multi-target scan correlation."""

from agent.detection.detection_models import DetectionMethodEnum, SeverityEnum
from agent.risk.alert_correlation import AlertCorrelator
from agent.risk.alert_models import Alert


def test_alert_correlation_multi_port_scan() -> None:
    """Test assigning correlation_id to multi-port scan sequence."""
    correlator = AlertCorrelator()

    a1 = Alert(
        detection_id="d1",
        agent_id="a1",
        flow_id="f1",
        src_ip="192.168.1.5",
        dst_ip="10.0.0.1",
        src_port=1000,
        dst_port=22,
        protocol="TCP",
        risk_score=70.0,
        severity=SeverityEnum.HIGH,
        detection_method=DetectionMethodEnum.SIGNATURE,
        confidence=0.8,
    )
    a2 = Alert(
        detection_id="d2",
        agent_id="a1",
        flow_id="f2",
        src_ip="192.168.1.5",
        dst_ip="10.0.0.1",
        src_port=1001,
        dst_port=80,
        protocol="TCP",
        risk_score=70.0,
        severity=SeverityEnum.HIGH,
        detection_method=DetectionMethodEnum.SIGNATURE,
        confidence=0.8,
    )
    a3 = Alert(
        detection_id="d3",
        agent_id="a1",
        flow_id="f3",
        src_ip="192.168.1.5",
        dst_ip="10.0.0.1",
        src_port=1002,
        dst_port=443,
        protocol="TCP",
        risk_score=70.0,
        severity=SeverityEnum.HIGH,
        detection_method=DetectionMethodEnum.SIGNATURE,
        confidence=0.8,
    )

    correlator.correlate(a1)
    correlator.correlate(a2)
    c3 = correlator.correlate(a3)

    assert c3.correlation_id is not None
    assert "corr-scan-" in c3.correlation_id
