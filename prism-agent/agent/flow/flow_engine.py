"""Master Flow Generation Engine Lifecycle Controller."""

from typing import Any, Dict, Optional
import structlog
from agent.capture.packet_queue import PacketQueue
from agent.core.config import agent_settings
from agent.flow.flow_manager import FlowManager
from agent.flow.flow_queue import FlowQueue
from agent.flow.flow_statistics import FlowStatistics
from agent.flow.flow_table import FlowTable

logger = structlog.get_logger("prism_agent.flow_engine")


class FlowEngine:
    """High-level Flow Generation Engine coordinating flow aggregation, expiration, and output queueing."""

    def __init__(self, packet_queue: Optional[PacketQueue] = None) -> None:
        self.packet_queue = packet_queue
        self.output_queue = FlowQueue(maxsize=agent_settings.FLOW_QUEUE_MAX_SIZE)
        self.flow_table = FlowTable(max_size=agent_settings.FLOW_TABLE_MAX_SIZE)
        self.statistics = FlowStatistics()
        self.manager: Optional[FlowManager] = None

        self._is_initialized: bool = False
        self._is_running: bool = False

    def bind_packet_queue(self, packet_queue: PacketQueue) -> None:
        """Bind input PacketQueue from Capture Engine."""
        self.packet_queue = packet_queue
        self._is_initialized = True

    async def start(self) -> None:
        """Start Flow Generation Engine."""
        if not self.packet_queue:
            raise RuntimeError("Cannot start FlowEngine without a bound PacketQueue")

        if self._is_running:
            logger.warning("FlowEngine is already running")
            return

        self.manager = FlowManager(
            input_packet_queue=self.packet_queue,
            output_flow_queue=self.output_queue,
            flow_table=self.flow_table,
            statistics=self.statistics,
        )
        await self.manager.start()
        self._is_running = True
        logger.info("Flow Generation Engine started successfully")

    async def stop(self) -> None:
        """Stop Flow Generation Engine."""
        if self.manager:
            await self.manager.stop()
            self.manager = None
        self._is_running = False
        logger.info("Flow Generation Engine stopped")

    def get_status(self) -> Dict[str, Any]:
        """Return runtime state and metrics summary."""
        return {
            "initialized": self._is_initialized,
            "running": self._is_running,
            "active_flows": self.flow_table.active_count,
            "completed_queue_size": self.output_queue.size,
            "statistics": self.statistics.get_summary(self.flow_table.active_count),
        }
