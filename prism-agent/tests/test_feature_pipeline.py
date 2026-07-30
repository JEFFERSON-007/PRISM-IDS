"""Unit tests for FeaturePipeline end-to-end extraction from Flow."""

from agent.flow.flow_models import Flow
from agent.feature_extraction.feature_pipeline import FeaturePipeline


def test_feature_pipeline_extraction() -> None:
    """Test extracting complete FeatureVector from Flow."""
    flow = Flow(
        src_ip="192.168.1.50",
        dst_ip="8.8.8.8",
        src_port=53535,
        dst_port=53,
        protocol="UDP",
        forward_packets=2,
        backward_packets=2,
        forward_bytes=120,
        backward_bytes=240,
    )

    vec = FeaturePipeline.extract_features(flow)
    assert vec.flow_id == flow.flow_id
    assert vec.src_ip == "192.168.1.50"
    assert vec.dst_ip == "8.8.8.8"
    assert vec.service_name == "DNS"
    assert vec.total_packets == 4
    assert vec.total_bytes == 360
    assert vec.forward_bytes == 120
    assert vec.backward_bytes == 240
