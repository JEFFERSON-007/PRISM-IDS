"""Timing and Inter-Arrival Time (IAT) Feature Calculator."""

from typing import Dict, Any
from agent.flow.flow_models import Flow
from agent.feature_extraction.statistical_features import StatisticalFeatures


class TimingFeatures:
    """Calculates timing metrics and packet rate throughput."""

    @staticmethod
    def extract(flow: Flow) -> Dict[str, float]:
        """Extract duration, IAT stats, packets/sec, and bytes/sec."""
        dur = flow.duration_seconds
        tot_pkts = flow.total_packets
        tot_bytes = flow.total_bytes

        # Synthetic estimation of Inter-Arrival Times if packet-level timestamps aren't preserved
        if tot_pkts > 1 and dur > 0:
            avg_iat = dur / (tot_pkts - 1)
            min_iat = round(avg_iat * 0.5, 4)
            max_iat = round(avg_iat * 1.5, 4)
            std_iat = round(avg_iat * 0.2, 4)
            mean_iat = round(avg_iat, 4)
        else:
            mean_iat, min_iat, max_iat, std_iat = 0.0, 0.0, 0.0, 0.0

        packets_per_sec = round(tot_pkts / dur, 2) if dur > 0 else float(tot_pkts)
        bytes_per_sec = round(tot_bytes / dur, 2) if dur > 0 else float(tot_bytes)

        return {
            "duration": dur,
            "mean_iat": mean_iat,
            "min_iat": min_iat,
            "max_iat": max_iat,
            "std_iat": std_iat,
            "packets_per_sec": packets_per_sec,
            "bytes_per_sec": bytes_per_sec,
        }
