"""Unit tests for RiskEngine lifecycle."""

import pytest
from agent.detection.detection_queue import DetectionQueue
from agent.risk.risk_engine import RiskEngine


@pytest.mark.asyncio
async def test_risk_engine_start_stop() -> None:
    """Test RiskEngine binding and lifecycle."""
    det_q = DetectionQueue()
    engine = RiskEngine()
    engine.bind_detection_queue(det_q)

    await engine.start()
    status = engine.get_status()
    assert status["initialized"] is True
    assert status["running"] is True

    await engine.stop()
    status_after = engine.get_status()
    assert status_after["running"] is False
