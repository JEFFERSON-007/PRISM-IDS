"""Unit tests for SignatureEngine rule evaluation."""

from datetime import datetime, timezone
from agent.detection.signature_engine import SignatureEngine
from agent.feature_extraction.feature_models import FeatureVector


def test_signature_engine_syn_flood_match() -> None:
    """Test SYN flood signature rule match."""
    engine = SignatureEngine()

    now = datetime.now(timezone.utc)
    syn_flood_vector = FeatureVector(
        flow_id="f-syn",
        src_ip="192.168.1.10",
        dst_ip="10.0.0.1",
        src_port=1234,
        dst_port=80,
        protocol="TCP",
        start_time=now,
        end_time=now,
        duration=1.0,
        total_packets=50,
        forward_packets=50,
        backward_packets=0,
        total_bytes=3000,
        forward_bytes=3000,
        backward_bytes=0,
        min_pkt_len=60.0,
        max_pkt_len=60.0,
        mean_pkt_len=60.0,
        std_pkt_len=0.0,
        variance_pkt_len=0.0,
        mean_iat=0.02,
        min_iat=0.01,
        max_iat=0.03,
        std_iat=0.005,
        packets_per_sec=50.0,
        bytes_per_sec=3000.0,
        syn_count=50,
        ack_count=0,
        fin_count=0,
        rst_count=0,
        psh_count=0,
        urg_count=0,
        syn_ratio=1.0,
        ack_ratio=0.0,
        fwd_bwd_packet_ratio=50.0,
        fwd_bwd_byte_ratio=3000.0,
        avg_bytes_per_pkt=60.0,
        pkt_size_entropy=0.0,
        direction_entropy=0.0,
    )

    matches = engine.evaluate(syn_flood_vector)
    assert len(matches) > 0
    matched_ids = [m.rule_id for m in matches]
    assert "SIG-002" in matched_ids  # SYN Flood Rule
