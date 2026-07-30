"""Unit tests for FlowKey 5-tuple canonicalization and direction mapping."""

from agent.capture.packet_models import IPHeader, PacketProtocol, ParsedPacket, TCPFlags, TCPHeader
from agent.flow.flow_key import FlowDirection, FlowKey


def test_bidirectional_flow_key_canonicalization() -> None:
    """Test (A -> B) and (B -> A) generate identical FlowKey."""
    pkt1 = ParsedPacket(
        raw_length=60,
        protocol=PacketProtocol.TCP,
        ip_header=IPHeader(src_ip="192.168.1.10", dst_ip="10.0.0.1", version=4, ttl=64, protocol_number=6, length=60),
        tcp_header=TCPHeader(src_port=54321, dst_port=80, seq=1, ack=0, flags=TCPFlags(syn=True), window=65535),
    )

    pkt2 = ParsedPacket(
        raw_length=60,
        protocol=PacketProtocol.TCP,
        ip_header=IPHeader(src_ip="10.0.0.1", dst_ip="192.168.1.10", version=4, ttl=64, protocol_number=6, length=60),
        tcp_header=TCPHeader(src_port=80, dst_port=54321, seq=1, ack=1, flags=TCPFlags(syn=True, ack=True), window=65535),
    )

    key1, dir1 = FlowKey.from_packet(pkt1)
    key2, dir2 = FlowKey.from_packet(pkt2)

    assert key1 == key2
    assert dir1 != dir2
    assert {dir1, dir2} == {FlowDirection.FORWARD, FlowDirection.BACKWARD}
