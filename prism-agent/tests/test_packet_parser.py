"""Unit tests for Scapy Packet Parser."""

from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.l2 import Ether
from agent.capture.packet_models import PacketProtocol
from agent.capture.packet_parser import PacketParser


def test_parse_scapy_tcp_packet() -> None:
    """Test parsing synthetic TCP/IP packet."""
    pkt = Ether(src="00:11:22:33:44:55", dst="66:77:88:99:AA:BB") / IP(
        src="192.168.1.100", dst="10.0.0.1", ttl=64
    ) / TCP(sport=12345, dport=80, flags="S", seq=100)

    parsed = PacketParser.parse(pkt)
    assert parsed is not None
    assert parsed.protocol == PacketProtocol.TCP
    assert parsed.ip_header.src_ip == "192.168.1.100"
    assert parsed.ip_header.dst_ip == "10.0.0.1"
    assert parsed.tcp_header.src_port == 12345
    assert parsed.tcp_header.dst_port == 80
    assert parsed.tcp_header.flags.syn is True


def test_parse_scapy_udp_packet() -> None:
    """Test parsing synthetic UDP/IP packet."""
    pkt = Ether() / IP(src="1.1.1.1", dst="8.8.8.8") / UDP(sport=53, dport=5353)

    parsed = PacketParser.parse(pkt)
    assert parsed is not None
    assert parsed.protocol == PacketProtocol.UDP
    assert parsed.udp_header.src_port == 53
    assert parsed.udp_header.dst_port == 5353
