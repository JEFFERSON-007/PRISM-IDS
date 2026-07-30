"""Unit tests for Packet DTO Data Models."""

from agent.capture.packet_models import EthernetHeader, IPHeader, PacketProtocol, ParsedPacket, TCPFlags, TCPHeader


def test_parsed_packet_instantiation() -> None:
    """Test creating ParsedPacket DTO."""
    packet = ParsedPacket(
        raw_length=64,
        protocol=PacketProtocol.TCP,
        ip_header=IPHeader(
            src_ip="192.168.1.10",
            dst_ip="10.0.0.1",
            version=4,
            ttl=64,
            protocol_number=6,
            length=64,
        ),
        tcp_header=TCPHeader(
            src_port=443,
            dst_port=54321,
            seq=1000,
            ack=2000,
            flags=TCPFlags(syn=True, ack=True),
            window=65535,
        ),
    )
    assert packet.protocol == PacketProtocol.TCP
    assert packet.ip_header.src_ip == "192.168.1.10"
    assert packet.tcp_header.flags.syn is True
    assert packet.tcp_header.flags.ack is True
