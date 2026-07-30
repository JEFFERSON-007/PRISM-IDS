"""Flow Models and State Enums."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field
from agent.capture.packet_models import ParsedPacket
from agent.flow.flow_key import FlowDirection, FlowKey


class FlowState(str, Enum):
    """Flow lifecycle state."""

    ACTIVE = "ACTIVE"
    IDLE_TIMEOUT = "IDLE_TIMEOUT"
    ACTIVE_TIMEOUT = "ACTIVE_TIMEOUT"
    TCP_CLOSED = "TCP_CLOSED"


class TCPState(str, Enum):
    """TCP Connection state tracking."""

    LISTEN = "LISTEN"
    SYN_SENT = "SYN_SENT"
    SYN_RECEIVED = "SYN_RECEIVED"
    ESTABLISHED = "ESTABLISHED"
    FIN_WAIT = "FIN_WAIT"
    CLOSED = "CLOSED"


class Flow(BaseModel):
    """Aggregated bidirectional network flow model."""

    flow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str

    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    forward_packets: int = 0
    backward_packets: int = 0
    forward_bytes: int = 0
    backward_bytes: int = 0

    state: FlowState = FlowState.ACTIVE
    tcp_state: Optional[TCPState] = None

    # Cumulative TCP flag counts
    syn_count: int = 0
    ack_count: int = 0
    fin_count: int = 0
    rst_count: int = 0
    psh_count: int = 0
    urg_count: int = 0

    @property
    def total_packets(self) -> int:
        """Total packets in both directions."""
        return self.forward_packets + self.backward_packets

    @property
    def total_bytes(self) -> int:
        """Total payload and header bytes in both directions."""
        return self.forward_bytes + self.backward_bytes

    @property
    def duration_seconds(self) -> float:
        """Flow duration in seconds."""
        if not self.end_time or not self.start_time:
            return 0.0
        return max(0.0, round((self.end_time - self.start_time).total_seconds(), 3))

    def update(self, packet: ParsedPacket, direction: FlowDirection) -> None:
        """Update flow metrics with incoming packet."""
        pkt_time = packet.timestamp
        self.end_time = max(self.end_time, pkt_time)
        self.last_activity = max(self.last_activity, pkt_time)

        if direction == FlowDirection.FORWARD:
            self.forward_packets += 1
            self.forward_bytes += packet.raw_length
        else:
            self.backward_packets += 1
            self.backward_bytes += packet.raw_length

        # Update TCP Flags if TCP
        if packet.tcp_header:
            flags = packet.tcp_header.flags
            if flags.syn:
                self.syn_count += 1
            if flags.ack:
                self.ack_count += 1
            if flags.fin:
                self.fin_count += 1
            if flags.rst:
                self.rst_count += 1
            if flags.psh:
                self.psh_count += 1
            if flags.urg:
                self.urg_count += 1

            # Simple TCP state transition helper
            if flags.rst:
                self.tcp_state = TCPState.CLOSED
                self.state = FlowState.TCP_CLOSED
            elif flags.fin and self.fin_count >= 2:
                self.tcp_state = TCPState.CLOSED
                self.state = FlowState.TCP_CLOSED
            elif flags.syn and flags.ack:
                self.tcp_state = TCPState.ESTABLISHED
            elif flags.syn:
                self.tcp_state = TCPState.SYN_SENT
