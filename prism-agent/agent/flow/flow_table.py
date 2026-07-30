"""High-Performance In-Memory Flow Table for Active Flow Storage."""

from typing import Dict, List, Optional
import structlog
from agent.capture.packet_models import ParsedPacket
from agent.core.config import agent_settings
from agent.flow.flow_key import FlowDirection, FlowKey
from agent.flow.flow_models import Flow

logger = structlog.get_logger("prism_agent.flow_table")


class FlowTable:
    """Thread-safe in-memory hashmap for active bidirectional network flows."""

    def __init__(self, max_size: Optional[int] = None) -> None:
        self.max_size = max_size or agent_settings.FLOW_TABLE_MAX_SIZE
        self._table: Dict[FlowKey, Flow] = {}

    @property
    def active_count(self) -> int:
        """Return current number of active flows."""
        return len(self._table)

    def get_or_create(self, packet: ParsedPacket) -> Flow:
        """Find existing active flow by 5-tuple or instantiate new Flow."""
        flow_key, direction = FlowKey.from_packet(packet)

        if flow_key in self._table:
            flow = self._table[flow_key]
            flow.update(packet, direction)
            return flow

        # Overflow protection: enforce max active flow limit
        if len(self._table) >= self.max_size:
            logger.warning("Flow table at max capacity, rejecting new flow creation", active_count=len(self._table))

        new_flow = Flow(
            src_ip=flow_key.src_ip,
            dst_ip=flow_key.dst_ip,
            src_port=flow_key.src_port,
            dst_port=flow_key.dst_port,
            protocol=flow_key.protocol,
            start_time=packet.timestamp,
            end_time=packet.timestamp,
            last_activity=packet.timestamp,
        )
        new_flow.update(packet, direction)

        if len(self._table) < self.max_size:
            self._table[flow_key] = new_flow

        return new_flow

    def get_flow(self, flow_key: FlowKey) -> Optional[Flow]:
        """Fetch active flow by key."""
        return self._table.get(flow_key)

    def remove_flow(self, flow_key: FlowKey) -> Optional[Flow]:
        """Remove and return flow from table."""
        return self._table.pop(flow_key, None)

    def get_all_flows(self) -> List[Flow]:
        """Return list of all active flows."""
        return list(self._table.values())

    def get_all_keys(self) -> List[FlowKey]:
        """Return list of active flow keys."""
        return list(self._table.keys())

    def clear(self) -> None:
        """Clear flow table."""
        self._table.clear()
