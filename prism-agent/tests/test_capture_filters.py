"""Unit tests for BPF Builder and Validator."""

from agent.capture.capture_filters import BPFBuilder


def test_bpf_builder_construction() -> None:
    """Test building BPF string."""
    builder = BPFBuilder()
    builder.add_protocol("tcp").add_port(80).add_host("192.168.1.1")
    bpf_str = builder.build("and")
    assert "tcp" in bpf_str
    assert "port 80" in bpf_str
    assert "host 192.168.1.1" in bpf_str
    assert " and " in bpf_str


def test_validate_bpf() -> None:
    """Test BPF string validation."""
    assert BPFBuilder.validate_bpf("tcp and port 80") is True
    assert BPFBuilder.validate_bpf("ip or ip6") is True
    assert BPFBuilder.validate_bpf("tcp; rm -rf /") is False
