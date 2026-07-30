"""Packet Integrity and Validation Utilities."""

from typing import Tuple
from scapy.packet import Packet
import structlog

logger = structlog.get_logger("prism_agent.packet_validator")


class PacketValidator:
    """Validates raw packet integrity prior to deep header parsing."""

    MIN_PACKET_BYTES = 14  # Ethernet header min size

    @classmethod
    def is_valid_packet(cls, packet: Packet) -> Tuple[bool, str]:
        """Check if Scapy packet instance is well-formed and non-corrupted."""
        if not packet:
            return False, "Null packet instance"

        try:
            raw_len = len(packet)
            if raw_len < cls.MIN_PACKET_BYTES:
                return False, f"Packet size ({raw_len}B) below minimum Ethernet header limit"

            # Check if packet contains IP layer
            if not (packet.haslayer("IP") or packet.haslayer("IPv6") or packet.haslayer("ARP")):
                return False, "Non-IP / Non-ARP Link layer packet"

            return True, "Valid"
        except Exception as exc:
            logger.debug("Packet validation exception caught", error=str(exc))
            return False, f"Validation error: {str(exc)}"
