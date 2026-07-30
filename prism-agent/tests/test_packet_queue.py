"""Unit tests for bounded PacketQueue overflow behavior."""

from agent.capture.packet_models import PacketProtocol, ParsedPacket
from agent.capture.packet_queue import PacketQueue


def test_packet_queue_push_and_pop() -> None:
    """Test pushing and popping from queue."""
    q = PacketQueue(maxsize=5)
    assert q.size == 0

    pkt = ParsedPacket(raw_length=100, protocol=PacketProtocol.TCP)
    pushed = q.push_nowait(pkt)
    assert pushed is True
    assert q.size == 1


def test_packet_queue_overflow_drop() -> None:
    """Test queue drops oldest packet on overflow."""
    q = PacketQueue(maxsize=2)
    p1 = ParsedPacket(raw_length=10, protocol=PacketProtocol.TCP)
    p2 = ParsedPacket(raw_length=20, protocol=PacketProtocol.UDP)
    p3 = ParsedPacket(raw_length=30, protocol=PacketProtocol.ICMP)

    q.push_nowait(p1)
    q.push_nowait(p2)
    assert q.size == 2

    # Pushing 3rd packet should overflow and drop oldest p1
    q.push_nowait(p3)
    assert q.dropped_count >= 1
