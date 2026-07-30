"""Unit tests for FlowTable lookup and update operations."""

from agent.capture.packet_models import IPHeader, PacketProtocol, ParsedPacket, TCPFlags, TCPHeader
from agent.flow.flow_table import FlowTable


def test_flow_table_get_or_create() -> None:
    """Test FlowTable retrieves or instantiates flows."""
    table = FlowTable(max_size=10)
    assert table.active_count == 0

    pkt = ParsedPacket(
        raw_length=50,
        protocol=PacketProtocol.TCP,
        ip_header=IPHeader(src_ip="1.1.1.1", dst_ip="2.2.2.2", version=4, ttl=64, protocol_number=6, length=50),
        tcp_header=TCPHeader(src_port=100, dst_port=200, seq=1, flags=TCPFlags(), window=1000),
    )

    flow1 = table.get_or_create(pkt)
    assert table.active_count == 1
    assert flow1.total_packets == 1

    # Same packet should update existing flow in table
    flow2 = table.get_or_create(pkt)
    assert table.active_count == 1
    assert flow2.total_packets == 2
    assert flow1.flow_id == flow2.flow_id
