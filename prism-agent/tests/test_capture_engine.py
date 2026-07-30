"""Unit tests for CaptureEngine lifecycle."""

from agent.capture.capture_engine import CaptureEngine


def test_capture_engine_initialization() -> None:
    """Test engine initialization and status inspection."""
    engine = CaptureEngine()
    engine.initialize(bpf_filter="tcp port 80")
    status = engine.get_status()
    assert status["initialized"] is True
    assert status["bpf_filter"] == "tcp port 80"
    assert status["running"] is False


def test_capture_engine_pause_resume() -> None:
    """Test engine pause and resume toggle."""
    engine = CaptureEngine()
    engine.pause()
    assert engine._paused is True
    engine.resume()
    assert engine._paused is False
