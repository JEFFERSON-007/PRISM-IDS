"""Unit tests for FeatureValidator."""

from datetime import datetime, timezone
from agent.feature_extraction.feature_models import FeatureVector
from agent.feature_extraction.feature_validator import FeatureValidator


def test_feature_validator_clean_vector() -> None:
    """Test validating clean FeatureVector."""
    now = datetime.now(timezone.utc)
    vec = FeatureVector(
        flow_id="f1",
        src_ip="1.1.1.1",
        dst_ip="2.2.2.2",
        src_port=80,
        dst_port=123,
        protocol="UDP",
        start_time=now,
        end_time=now,
        duration=1.0,
        total_packets=2,
        forward_packets=1,
        backward_packets=1,
        total_bytes=100,
        forward_bytes=50,
        backward_bytes=50,
        min_pkt_len=50.0,
        max_pkt_len=50.0,
        mean_pkt_len=50.0,
        std_pkt_len=0.0,
        variance_pkt_len=0.0,
        mean_iat=1.0,
        min_iat=1.0,
        max_iat=1.0,
        std_iat=0.0,
        packets_per_sec=2.0,
        bytes_per_sec=100.0,
        syn_count=0,
        ack_count=0,
        fin_count=0,
        rst_count=0,
        psh_count=0,
        urg_count=0,
        syn_ratio=0.0,
        ack_ratio=0.0,
        fwd_bwd_packet_ratio=1.0,
        fwd_bwd_byte_ratio=1.0,
        avg_bytes_per_pkt=50.0,
        pkt_size_entropy=0.0,
        direction_entropy=1.0,
    )

    is_valid, sanitized, reason = FeatureValidator.validate_and_sanitize(vec)
    assert is_valid is True
    assert reason == "Valid"
