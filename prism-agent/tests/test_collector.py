"""Unit tests for system metric collector."""

from agent.system.collector import SystemCollector


def test_collect_static_info() -> None:
    """Test collector static information formatting."""
    info = SystemCollector.collect_static_info()
    assert "agent_name" in info
    assert "hostname" in info
    assert "operating_system" in info
    assert "version" in info


def test_collect_telemetry() -> None:
    """Test telemetry metric values bounds."""
    telemetry = SystemCollector.collect_telemetry()
    assert "cpu_usage" in telemetry
    assert 0.0 <= telemetry["cpu_usage"] <= 100.0
    assert 0.0 <= telemetry["ram_usage"] <= 100.0
    assert 0.0 <= telemetry["disk_usage"] <= 100.0
