"""TCP Control Flag and State Feature Calculator."""

from typing import Dict, Any
from agent.flow.flow_models import Flow


class TCPFeatures:
    """Calculates TCP control flag counts and flag distribution ratios."""

    @staticmethod
    def extract(flow: Flow) -> Dict[str, Any]:
        """Extract TCP flag counts and ratios."""
        if flow.protocol != "TCP":
            return {
                "syn_count": 0,
                "ack_count": 0,
                "fin_count": 0,
                "rst_count": 0,
                "psh_count": 0,
                "urg_count": 0,
                "syn_ratio": 0.0,
                "ack_ratio": 0.0,
            }

        tot_pkts = max(1, flow.total_packets)
        syn_ratio = round(flow.syn_count / tot_pkts, 3)
        ack_ratio = round(flow.ack_count / tot_pkts, 3)

        return {
            "syn_count": flow.syn_count,
            "ack_count": flow.ack_count,
            "fin_count": flow.fin_count,
            "rst_count": flow.rst_count,
            "psh_count": flow.psh_count,
            "urg_count": flow.urg_count,
            "syn_ratio": syn_ratio,
            "ack_ratio": ack_ratio,
        }
