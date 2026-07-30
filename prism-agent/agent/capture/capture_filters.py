"""Berkeley Packet Filter (BPF) Syntax Construction and Validation."""

import re
from typing import List, Optional
import structlog

logger = structlog.get_logger("prism_agent.capture_filters")


class BPFBuilder:
    """Helper to build and validate BPF expressions."""

    def __init__(self) -> None:
        self._conditions: List[str] = []

    def add_protocol(self, protocol: str) -> "BPFBuilder":
        """Add protocol filter (e.g. tcp, udp, icmp, arp)."""
        proto = protocol.lower().strip()
        if proto in ("tcp", "udp", "icmp", "arp", "ip", "ip6"):
            self._conditions.append(proto)
        return self

    def add_port(self, port: int, direction: Optional[str] = None) -> "BPFBuilder":
        """Add port filter (e.g. port 80, src port 443)."""
        if 0 <= port <= 65535:
            if direction in ("src", "dst"):
                self._conditions.append(f"{direction} port {port}")
            else:
                self._conditions.append(f"port {port}")
        return self

    def add_host(self, host: str, direction: Optional[str] = None) -> "BPFBuilder":
        """Add IP host filter (e.g. host 192.168.1.1, src host 10.0.0.1)."""
        if direction in ("src", "dst"):
            self._conditions.append(f"{direction} host {host}")
        else:
            self._conditions.append(f"host {host}")
        return self

    def build(self, logical_op: str = "and") -> str:
        """Combine filter conditions into a valid BPF string."""
        if not self._conditions:
            return "ip or ip6"
        op = f" {logical_op.strip()} "
        return op.join(self._conditions)

    @staticmethod
    def validate_bpf(bpf_string: str) -> bool:
        """Sanity check BPF filter string syntax."""
        if not bpf_string or not bpf_string.strip():
            return True
        # Check basic illegal character injection
        illegal_pattern = re.compile(r"[;`$><]")
        if illegal_pattern.search(bpf_string):
            logger.warning("Invalid characters detected in BPF filter string", bpf_filter=bpf_string)
            return False
        return True
