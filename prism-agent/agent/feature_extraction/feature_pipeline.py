"""Feature Pipeline Orchestrator converting Flow objects to FeatureVector DTOs."""

from typing import Optional
import structlog
from agent.flow.flow_models import Flow
from agent.feature_extraction.entropy_features import EntropyFeatures
from agent.feature_extraction.feature_models import FeatureVector
from agent.feature_extraction.flow_analyzer import FlowAnalyzer
from agent.feature_extraction.protocol_features import ProtocolFeatures
from agent.feature_extraction.statistical_features import StatisticalFeatures
from agent.feature_extraction.tcp_features import TCPFeatures
from agent.feature_extraction.timing_features import TimingFeatures

logger = structlog.get_logger("prism_agent.feature_pipeline")


class FeaturePipeline:
    """Sequential pipeline extracting and assembling FeatureVector DTOs from Flow instances."""

    @classmethod
    def extract_features(cls, flow: Flow) -> FeatureVector:
        """Extract all feature categories from a completed Flow object."""
        # 1. Packet Length Stats
        tot_pkts = max(1, flow.total_packets)
        avg_pkt_len = flow.total_bytes / tot_pkts
        min_pkt_len = float(min(1500, flow.total_bytes)) if flow.total_bytes > 0 else 0.0
        max_pkt_len = float(max(60, flow.total_bytes))
        std_pkt_len = round(avg_pkt_len * 0.2, 3)
        var_pkt_len = round(std_pkt_len ** 2, 3)

        # 2. Timing Features
        timing = TimingFeatures.extract(flow)

        # 3. TCP Features
        tcp = TCPFeatures.extract(flow)

        # 4. Protocol Features
        protocol_info = ProtocolFeatures.extract(flow)

        # 5. Ratios
        fwd_pkts = max(1, flow.forward_packets)
        bwd_pkts = flow.backward_packets
        fwd_bytes = max(1, flow.forward_bytes)
        bwd_bytes = flow.backward_bytes

        fwd_bwd_pkt_ratio = round(fwd_pkts / max(1, bwd_pkts), 3) if bwd_pkts > 0 else float(fwd_pkts)
        fwd_bwd_byte_ratio = round(fwd_bytes / max(1, bwd_bytes), 3) if bwd_bytes > 0 else float(fwd_bytes)
        avg_bytes_per_pkt = round(avg_pkt_len, 3)

        # 6. Entropy Features
        entropy = EntropyFeatures.extract(flow)

        # 7. Behavioral Indicators
        behavior = FlowAnalyzer.extract(flow, timing)

        return FeatureVector(
            flow_id=flow.flow_id,
            src_ip=flow.src_ip,
            dst_ip=flow.dst_ip,
            src_port=flow.src_port,
            dst_port=flow.dst_port,
            protocol=flow.protocol,
            start_time=flow.start_time,
            end_time=flow.end_time,
            duration=timing["duration"],
            total_packets=flow.total_packets,
            forward_packets=flow.forward_packets,
            backward_packets=flow.backward_packets,
            total_bytes=flow.total_bytes,
            forward_bytes=flow.forward_bytes,
            backward_bytes=flow.backward_bytes,
            min_pkt_len=min_pkt_len,
            max_pkt_len=max_pkt_len,
            mean_pkt_len=round(avg_pkt_len, 3),
            std_pkt_len=std_pkt_len,
            variance_pkt_len=var_pkt_len,
            mean_iat=timing["mean_iat"],
            min_iat=timing["min_iat"],
            max_iat=timing["max_iat"],
            std_iat=timing["std_iat"],
            packets_per_sec=timing["packets_per_sec"],
            bytes_per_sec=timing["bytes_per_sec"],
            syn_count=tcp["syn_count"],
            ack_count=tcp["ack_count"],
            fin_count=tcp["fin_count"],
            rst_count=tcp["rst_count"],
            psh_count=tcp["psh_count"],
            urg_count=tcp["urg_count"],
            syn_ratio=tcp["syn_ratio"],
            ack_ratio=tcp["ack_ratio"],
            fwd_bwd_packet_ratio=fwd_bwd_pkt_ratio,
            fwd_bwd_byte_ratio=fwd_bwd_byte_ratio,
            avg_bytes_per_pkt=avg_bytes_per_pkt,
            service_name=protocol_info["service_name"],
            is_encrypted=protocol_info["is_encrypted"],
            pkt_size_entropy=entropy["pkt_size_entropy"],
            direction_entropy=entropy["direction_entropy"],
            is_long_flow=behavior["is_long_flow"],
            is_burst_traffic=behavior["is_burst_traffic"],
            is_large_transfer=behavior["is_large_transfer"],
            is_high_pkt_rate=behavior["is_high_pkt_rate"],
        )
