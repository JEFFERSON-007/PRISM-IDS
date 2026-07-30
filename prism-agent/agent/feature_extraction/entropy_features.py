"""Shannon Entropy Feature Calculator for Packet Distributions."""

import math
from typing import Dict, List
from agent.flow.flow_models import Flow


class EntropyFeatures:
    """Calculates Shannon entropy on traffic metrics."""

    @staticmethod
    def calculate_shannon_entropy(probabilities: List[float]) -> float:
        """Compute Shannon entropy H(X) = -sum(p * log2(p))."""
        entropy = 0.0
        for p in probabilities:
            if p > 0:
                entropy -= p * math.log2(p)
        return round(entropy, 3)

    @classmethod
    def extract(cls, flow: Flow) -> Dict[str, float]:
        """Compute direction and size entropy for flow."""
        tot_pkts = flow.total_packets
        if tot_pkts <= 0:
            return {"pkt_size_entropy": 0.0, "direction_entropy": 0.0}

        # Direction entropy (forward vs backward ratio entropy)
        p_fwd = flow.forward_packets / tot_pkts
        p_bwd = flow.backward_packets / tot_pkts
        direction_entropy = cls.calculate_shannon_entropy([p_fwd, p_bwd])

        # Estimate packet size entropy based on average bytes distribution
        avg_b = flow.total_bytes / tot_pkts if tot_pkts > 0 else 0
        p_small = min(1.0, max(0.0, 1.0 - (avg_b / 1500.0)))
        p_large = 1.0 - p_small
        pkt_size_entropy = cls.calculate_shannon_entropy([p_small, p_large])

        return {
            "pkt_size_entropy": pkt_size_entropy,
            "direction_entropy": direction_entropy,
        }
