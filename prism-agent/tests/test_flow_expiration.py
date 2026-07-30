"""Unit tests for FlowExpirationService."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
import pytest
from agent.capture.packet_models import IPHeader, PacketProtocol, ParsedPacket, TCPFlags, TCPHeader
from agent.flow.flow_expiration import FlowExpirationService
from agent.flow.flow_models import FlowState
from agent.flow.flow_queue import FlowQueue
from agent.flow.flow_statistics import FlowStatistics
from agent.flow.flow_table import FlowTable


@pytest.mark.asyncio
async def test_flow_idle_expiration() -> None:
    """Test expiring flows exceeding idle timeout."""
    table = FlowTable()
    output_q = FlowQueue()
    stats = FlowStatistics()

    service = FlowExpirationService(flow_table=table, output_queue=output_q, statistics=stats)
    service.idle_timeout = 5.0  # 5 seconds

    old_pkt = ParsedPacket(
        timestamp=datetime.now(timezone.utc) - timedelta(seconds=10),
        raw_length=60,
        protocol=PacketProtocol.TCP,
        ip_header=IPHeader(src_ip="10.0.0.1", dst_ip="10.0.0.2", version=4, ttl=64, protocol_number=6, length=60),
        tcp_header=TCPHeader(src_port=80, dst_port=123, seq=1, flags=TCPFlags(), window=100),
    )

    table.get_or_create(old_pkt)
    assert table.active_count == 1

    expired_count = await service.sweep_expired_flows()
    assert expired_count == 1
    assert table.active_count == 0
    assert output_q.size == 1

    completed_flow = await output_q.get()
    assert completed_flow.state == FlowState.IDLE_TIMEOUT
