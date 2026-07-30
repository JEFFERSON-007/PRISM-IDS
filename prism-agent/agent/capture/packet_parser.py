"""Packet Parser converting raw Scapy packets to strongly typed ParsedPacket DTOs."""

from datetime import datetime, timezone
from typing import Optional
from scapy.packet import Packet, Raw
import structlog

from agent.capture.packet_models import (
    EthernetHeader,
    ICMPHeader,
    IPHeader,
    PacketProtocol,
    ParsedPacket,
    TCPFlags,
    TCPHeader,
    UDPHeader,
)
from agent.capture.packet_validator import PacketValidator

logger = structlog.get_logger("prism_agent.packet_parser")


class PacketParser:
    """Extracts structured header fields from Scapy Packet instances."""

    @classmethod
    def parse(cls, packet: Packet) -> Optional[ParsedPacket]:
        """Parse a Scapy packet into a ParsedPacket object, returning None if invalid or unparsable."""
        is_valid, reason = PacketValidator.is_valid_packet(packet)
        if not is_valid:
            logger.debug("Discarded invalid packet", reason=reason)
            return None

        try:
            timestamp = datetime.fromtimestamp(float(packet.time), tz=timezone.utc)
            raw_len = len(packet)

            # Ethernet Layer
            eth_header: Optional[EthernetHeader] = None
            if packet.haslayer("Ether"):
                eth_layer = packet.getlayer("Ether")
                eth_header = EthernetHeader(
                    src_mac=eth_layer.src,
                    dst_mac=eth_layer.dst,
                    ethertype=eth_layer.type,
                )

            # IP Layer (v4 / v6)
            ip_header: Optional[IPHeader] = None
            proto_enum = PacketProtocol.OTHER

            if packet.haslayer("IP"):
                ip = packet.getlayer("IP")
                ip_header = IPHeader(
                    src_ip=ip.src,
                    dst_ip=ip.dst,
                    version=4,
                    ttl=ip.ttl,
                    protocol_number=ip.proto,
                    length=ip.len,
                    id=ip.id,
                )
            elif packet.haslayer("IPv6"):
                ip6 = packet.getlayer("IPv6")
                ip_header = IPHeader(
                    src_ip=ip6.src,
                    dst_ip=ip6.dst,
                    version=6,
                    ttl=ip6.hlim,
                    protocol_number=ip6.nh,
                    length=ip6.plen,
                    id=None,
                )

            # Transport Layer (TCP / UDP / ICMP / ARP)
            tcp_header: Optional[TCPHeader] = None
            udp_header: Optional[UDPHeader] = None
            icmp_header: Optional[ICMPHeader] = None

            if packet.haslayer("TCP"):
                proto_enum = PacketProtocol.TCP
                tcp = packet.getlayer("TCP")
                flags_int = int(tcp.flags)
                tcp_flags = TCPFlags(
                    syn=bool(flags_int & 0x02),
                    ack=bool(flags_int & 0x10),
                    fin=bool(flags_int & 0x01),
                    rst=bool(flags_int & 0x04),
                    psh=bool(flags_int & 0x08),
                    urg=bool(flags_int & 0x20),
                )
                tcp_header = TCPHeader(
                    src_port=tcp.sport,
                    dst_port=tcp.dport,
                    seq=tcp.seq,
                    ack=tcp.ack,
                    flags=tcp_flags,
                    window=tcp.window,
                )
            elif packet.haslayer("UDP"):
                proto_enum = PacketProtocol.UDP
                udp = packet.getlayer("UDP")
                udp_header = UDPHeader(
                    src_port=udp.sport,
                    dst_port=udp.dport,
                    length=udp.len,
                )
            elif packet.haslayer("ICMP"):
                proto_enum = PacketProtocol.ICMP
                icmp = packet.getlayer("ICMP")
                icmp_header = ICMPHeader(type=icmp.type, code=icmp.code)
            elif packet.haslayer("ARP"):
                proto_enum = PacketProtocol.ARP

            # Extract Payload Snippet
            payload_snippet: Optional[str] = None
            payload_len = 0
            if packet.haslayer(Raw):
                raw_payload = packet.getlayer(Raw).load
                payload_len = len(raw_payload)
                payload_snippet = raw_payload[:64].hex()

            return ParsedPacket(
                timestamp=timestamp,
                raw_length=raw_len,
                protocol=proto_enum,
                eth_header=eth_header,
                ip_header=ip_header,
                tcp_header=tcp_header,
                udp_header=udp_header,
                icmp_header=icmp_header,
                payload_length=payload_len,
                payload_snippet=payload_snippet,
            )

        except Exception as exc:
            logger.error("Failed to parse packet", error=str(exc))
            return None
