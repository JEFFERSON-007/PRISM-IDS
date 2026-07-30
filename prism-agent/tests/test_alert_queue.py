"""Unit tests for AlertQueue buffer."""

import pytest
from agent.detection.detection_models import DetectionMethodEnum, SeverityEnum
from agent.risk.alert_models import Alert
from agent.risk.alert_queue import AlertQueue


@pytest.mark.asyncio
async def test_alert_queue_push_and_pop() -> None:
    """Test pushing and popping Alert objects."""
    aq = AlertQueue(maxsize=5)
    assert aq.size == 0

    alert = Alert(
        detection_id="d1",
        agent_id="a1",
        flow_id="f1",
        src_ip="1.1.1.1",
        dst_ip="2.2.2.2",
        src_port=10,
        dst_port=20,
        protocol="TCP",
        risk_score=50.0,
        severity=SeverityEnum.MEDIUM,
        detection_method=DetectionMethodEnum.SIGNATURE,
        confidence=0.7,
    )

    pushed = aq.push_nowait(alert)
    assert pushed is True
    assert aq.size == 1

    popped = await aq.get()
    assert popped.alert_id == alert.alert_id
