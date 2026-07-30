"""Unit tests for Flow DTO metric accumulators."""

from agent.capture.packet_models import IPHeader, PacketProtocol, ParsedPacket, TCPFlags, TCPHeader
from agent.flow.flow_key import FlowDirection
from agent.flow.flow_models import Flow


def test_flow_metric_accumulation() -> None:
    """Test updating flow metrics for forward and backward packets."""
    flow = Flow(src_ip="10.0.0.1", dst_ip="192.168.1.1", src_port=80, dst_port=12345, protocol="TCP")
    assert flow.total_packets == 0

    fwd_pkt = ParsedPacket(
        raw_length=100,
        protocol=PacketProtocol.TCP,
        ip_header=IPHeader(src_ip="10.0.0.1", dst_ip="192.168.1.1", version=4, ttl=64, protocol_number=6, length=100),
        tcp_header=TCPHeader(src_port=80, dst_port=12345, seq=1, ack=0, flags=TCPFlags(syn=True), window=65535),
    )
    bwd_pkt = ParsedPacket(
        raw_length=200,
        protocol=PacketProtocol.TCP,
        ip_header=IPHeader(src_ip="192.168.1.1", dst_ip="10.0.0.1", version=4, ttl=64, protocol_number=6, length=200),
        tcp_header=TCPHeader(src_port=12345, dst_port=80, seq=1, ack=1, flags=TCPFlags(syn=True, ack=True), window=65535),
    )

    flow.update(fwd_pkt, FlowDirection.FORWARD)
    flow.update(bwd_pkt, FlowDirection.BACKWARD)

    assert flow.forward_packets == 1
    assert flow.backward_packets == 1
    assert flow.total_packets == 2
    assert flow.forward_bytes == 100
    assert flow.backward_bytes == 200
    assert flow.total_bytes == 300
    assert flow.syn_count == 2
    assert flow.ack_count == 1
