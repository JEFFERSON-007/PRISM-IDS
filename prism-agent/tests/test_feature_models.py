"""Unit tests for FeatureVector DTO serialization methods."""

from datetime import datetime, timezone
from agent.feature_extraction.feature_models import FeatureVector


def test_feature_vector_serialization() -> None:
    """Test converting FeatureVector to dict, json, and numpy array."""
    now = datetime.now(timezone.utc)
    vec = FeatureVector(
        flow_id="test-uuid",
        src_ip="192.168.1.10",
        dst_ip="10.0.0.1",
        src_port=1234,
        dst_port=80,
        protocol="TCP",
        start_time=now,
        end_time=now,
        duration=1.5,
        total_packets=10,
        forward_packets=6,
        backward_packets=4,
        total_bytes=1000,
        forward_bytes=600,
        backward_bytes=400,
        min_pkt_len=60.0,
        max_pkt_len=1500.0,
        mean_pkt_len=100.0,
        std_pkt_len=20.0,
        variance_pkt_len=400.0,
        mean_iat=0.15,
        min_iat=0.05,
        max_iat=0.3,
        std_iat=0.02,
        packets_per_sec=6.67,
        bytes_per_sec=666.67,
        syn_count=1,
        ack_count=9,
        fin_count=0,
        rst_count=0,
        psh_count=2,
        urg_count=0,
        syn_ratio=0.1,
        ack_ratio=0.9,
        fwd_bwd_packet_ratio=1.5,
        fwd_bwd_byte_ratio=1.5,
        avg_bytes_per_pkt=100.0,
        service_name="HTTP",
        is_encrypted=False,
        pkt_size_entropy=0.5,
        direction_entropy=0.97,
        is_long_flow=False,
        is_burst_traffic=False,
        is_large_transfer=False,
        is_high_pkt_rate=False,
    )

    d = vec.to_dict()
    assert isinstance(d, dict)
    assert d["flow_id"] == "test-uuid"
    assert d["service_name"] == "HTTP"

    json_str = vec.to_json()
    assert isinstance(json_str, str)
    assert "192.168.1.10" in json_str

    arr = vec.to_numpy_list()
    assert isinstance(arr, list)
    assert len(arr) > 20
    assert arr[0] == 1.5
