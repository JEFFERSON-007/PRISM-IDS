"""Flow Manager executing continuous packet consumption and flow aggregation."""

import asyncio
from typing import Optional
import structlog
from agent.capture.packet_models import ParsedPacket
from agent.capture.packet_queue import PacketQueue
from agent.flow.flow_expiration import FlowExpirationService
from agent.flow.flow_queue import FlowQueue
from agent.flow.flow_statistics import FlowStatistics
from agent.flow.flow_table import FlowTable

logger = structlog.get_logger("prism_agent.flow_manager")


class FlowManager:
    """Consumes packets from PacketQueue and aggregates bidirectional Flow objects."""

    def __init__(
        self,
        input_packet_queue: PacketQueue,
        output_flow_queue: FlowQueue,
        flow_table: FlowTable,
        statistics: FlowStatistics,
    ) -> None:
        self.packet_queue = input_packet_queue
        self.output_flow_queue = output_flow_queue
        self.flow_table = flow_table
        self.statistics = statistics

        self.expiration_service = FlowExpirationService(
            flow_table=self.flow_table,
            output_queue=self.output_flow_queue,
            statistics=self.statistics,
        )

        self._running: bool = False
        self._consumer_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start packet consumer worker and flow expiration daemon."""
        self._running = True
        self.statistics.start()
        await self.expiration_service.start()
        self._consumer_task = asyncio.create_task(self._packet_consumer_loop())
        logger.info("Flow Manager packet consumer loop started")

    async def stop(self) -> None:
        """Stop packet consumer worker and flow expiration daemon."""
        self._running = False
        if self._consumer_task:
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass

        await self.expiration_service.stop()
        self.statistics.stop()
        logger.info("Flow Manager stopped")

    async def _packet_consumer_loop(self) -> None:
        """Continuous async consumer popping packets from PacketQueue."""
        while self._running:
            try:
                packet: ParsedPacket = await self.packet_queue.get()
                self._process_packet(packet)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self.statistics.record_error()
                logger.error("Error processing packet in flow aggregator", error=str(exc))

    def _process_packet(self, packet: ParsedPacket) -> None:
        """Update or instantiate flow from packet."""
        initial_count = self.flow_table.active_count
        flow = self.flow_table.get_or_create(packet)
        self.statistics.record_packet(packet.raw_length)

        if self.flow_table.active_count > initial_count:
            self.statistics.record_flow_created()
            logger.debug("Created new flow", flow_id=flow.flow_id, protocol=flow.protocol)
