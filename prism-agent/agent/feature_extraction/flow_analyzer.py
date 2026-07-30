"""Behavioral Traffic Indicator Extractor."""

from typing import Dict, Any
from agent.flow.flow_models import Flow


class FlowAnalyzer:
    """Evaluates behavioral flags and operational patterns on network flows."""

    @staticmethod
    def extract(flow: Flow, timing_stats: Dict[str, float]) -> Dict[str, bool]:
        """Extract behavioral indicators."""
        duration = flow.duration_seconds
        tot_bytes = flow.total_bytes
        pps = timing_stats.get("packets_per_sec", 0.0)

        is_long_flow = duration >= 60.0
        is_large_transfer = tot_bytes >= 1_000_000  # >= 1MB
        is_high_pkt_rate = pps >= 100.0
        is_burst_traffic = pps >= 50.0 and duration <= 2.0

        return {
            "is_long_flow": is_long_flow,
            "is_burst_traffic": is_burst_traffic,
            "is_large_transfer": is_large_transfer,
            "is_high_pkt_rate": is_high_pkt_rate,
        }
