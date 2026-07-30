"""Canonical 5-Tuple Flow Key for Bidirectional Flow Identification."""

from dataclasses import dataclass
from enum import Enum
from typing import Tuple
from agent.capture.packet_models import ParsedPacket


class FlowDirection(str, Enum):
    """Direction relative to flow creation."""

    FORWARD = "FORWARD"
    BACKWARD = "BACKWARD"


@dataclass(frozen=True)
class FlowKey:
    """Immutable hashable canonical 5-tuple key: (src_ip, dst_ip, src_port, dst_port, protocol)."""

    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str

    @classmethod
    def from_packet(cls, packet: ParsedPacket) -> Tuple["FlowKey", FlowDirection]:
        """Extract canonical 5-tuple FlowKey and packet direction from ParsedPacket."""
        if not packet.ip_header:
            src_ip, dst_ip = "0.0.0.0", "0.0.0.0"
        else:
            src_ip, dst_ip = packet.ip_header.src_ip, packet.ip_header.dst_ip

        src_port, dst_port = 0, 0
        if packet.tcp_header:
            src_port, dst_port = packet.tcp_header.src_port, packet.tcp_header.dst_port
        elif packet.udp_header:
            src_port, dst_port = packet.udp_header.src_port, packet.udp_header.dst_port

        proto_str = packet.protocol.value

        # Standardize canonical representation: lower IP address or lower port comes first
        if (src_ip, src_port) <= (dst_ip, dst_port):
            canonical_key = cls(
                src_ip=src_ip,
                dst_ip=dst_ip,
                src_port=src_port,
                dst_port=dst_port,
                protocol=proto_str,
            )
            direction = FlowDirection.FORWARD
        else:
            canonical_key = cls(
                src_ip=dst_ip,
                dst_ip=src_ip,
                src_port=dst_port,
                dst_port=src_port,
                protocol=proto_str,
            )
            direction = FlowDirection.BACKWARD

        return canonical_key, direction
