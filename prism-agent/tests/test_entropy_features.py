"""Unit tests for Shannon Entropy calculation."""

from agent.flow.flow_models import Flow
from agent.feature_extraction.entropy_features import EntropyFeatures


def test_shannon_entropy_balanced() -> None:
    """Test equal probabilities produce maximum binary entropy of 1.0."""
    entropy = EntropyFeatures.calculate_shannon_entropy([0.5, 0.5])
    assert round(entropy, 2) == 1.0


def test_shannon_entropy_flow() -> None:
    """Test extracting direction entropy from Flow."""
    flow = Flow(
        src_ip="10.0.0.1",
        dst_ip="10.0.0.2",
        src_port=80,
        dst_port=1234,
        protocol="TCP",
        forward_packets=5,
        backward_packets=5,
        forward_bytes=500,
        backward_bytes=500,
    )

    entropy_dict = EntropyFeatures.extract(flow)
    assert "direction_entropy" in entropy_dict
    assert round(entropy_dict["direction_entropy"], 2) == 1.0
