"""Unit tests for DetectionFusion merging."""

from datetime import datetime, timezone
from agent.detection.detection_fusion import DetectionFusion
from agent.detection.detection_models import DetectionMethodEnum, MLPredictionResult, RuleMatch, SeverityEnum
from agent.feature_extraction.feature_models import FeatureVector


def test_detection_fusion_hybrid() -> None:
    """Test fusing Signature and ML positive into HYBRID DetectionResult."""
    now = datetime.now(timezone.utc)
    vec = FeatureVector(
        flow_id="f-fuse",
        src_ip="1.1.1.1",
        dst_ip="2.2.2.2",
        src_port=80,
        dst_port=100,
        protocol="TCP",
        start_time=now,
        end_time=now,
        duration=1.0,
        total_packets=10,
        forward_packets=5,
        backward_packets=5,
        total_bytes=500,
        forward_bytes=250,
        backward_bytes=250,
        min_pkt_len=50.0,
        max_pkt_len=50.0,
        mean_pkt_len=50.0,
        std_pkt_len=0.0,
        variance_pkt_len=0.0,
        mean_iat=0.1,
        min_iat=0.1,
        max_iat=0.1,
        std_iat=0.0,
        packets_per_sec=10.0,
        bytes_per_sec=500.0,
        syn_count=1,
        ack_count=9,
        fin_count=0,
        rst_count=0,
        psh_count=0,
        urg_count=0,
        syn_ratio=0.1,
        ack_ratio=0.9,
        fwd_bwd_packet_ratio=1.0,
        fwd_bwd_byte_ratio=1.0,
        avg_bytes_per_pkt=50.0,
        pkt_size_entropy=0.0,
        direction_entropy=1.0,
    )

    rules = [RuleMatch(rule_id="SIG-001", name="Rule1", severity=SeverityEnum.HIGH, evidence={})]
    ml = MLPredictionResult(is_malicious=True, probability=0.95, confidence=0.95)

    detection = DetectionFusion.fuse(vec, rules, ml)
    assert detection is not None
    assert detection.detection_method == DetectionMethodEnum.HYBRID
    assert detection.severity == SeverityEnum.CRITICAL
