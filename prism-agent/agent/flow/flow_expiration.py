"""Background Flow Expiration and Cleanup Daemon."""

import asyncio
from datetime import datetime, timezone
from typing import List, Optional
import structlog
from agent.core.config import agent_settings
from agent.flow.flow_key import FlowKey
from agent.flow.flow_models import Flow, FlowState
from agent.flow.flow_queue import FlowQueue
from agent.flow.flow_statistics import FlowStatistics
from agent.flow.flow_table import FlowTable

logger = structlog.get_logger("prism_agent.flow_expiration")


class FlowExpirationService:
    """Scans active flow table and expires flows exceeding idle, active, or TCP termination criteria."""

    def __init__(
        self,
        flow_table: FlowTable,
        output_queue: FlowQueue,
        statistics: FlowStatistics,
    ) -> None:
        self.flow_table = flow_table
        self.output_queue = output_queue
        self.statistics = statistics

        self.idle_timeout = agent_settings.FLOW_IDLE_TIMEOUT
        self.active_timeout = agent_settings.FLOW_ACTIVE_TIMEOUT
        self.cleanup_interval = agent_settings.FLOW_CLEANUP_INTERVAL

        self._running: bool = False
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start background flow expiration task."""
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info(
            "Flow expiration daemon started",
            idle_timeout=self.idle_timeout,
            active_timeout=self.active_timeout,
            cleanup_interval=self.cleanup_interval,
        )

    async def stop(self) -> None:
        """Stop background flow expiration task."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Flow expiration daemon stopped")

    async def _run_loop(self) -> None:
        """Continuous cleanup execution loop."""
        while self._running:
            try:
                await self.sweep_expired_flows()
            except Exception as exc:
                logger.error("Error during flow expiration sweep", error=str(exc))

            try:
                await asyncio.sleep(self.cleanup_interval)
            except asyncio.CancelledError:
                break

    async def sweep_expired_flows(self) -> int:
        """Scan active table, expire matching flows, and push to output queue."""
        now = datetime.now(timezone.utc)
        expired_keys: List[FlowKey] = []
        expired_flows: List[Flow] = []

        all_keys = self.flow_table.get_all_keys()

        for key in all_keys:
            flow = self.flow_table.get_flow(key)
            if not flow:
                continue

            idle_duration = (now - flow.last_activity).total_seconds()
            active_duration = (now - flow.start_time).total_seconds()

            is_expired = False

            if flow.state == FlowState.TCP_CLOSED:
                is_expired = True
            elif idle_duration >= self.idle_timeout:
                flow.state = FlowState.IDLE_TIMEOUT
                is_expired = True
            elif active_duration >= self.active_timeout:
                flow.state = FlowState.ACTIVE_TIMEOUT
                is_expired = True

            if is_expired:
                expired_keys.append(key)
                expired_flows.append(flow)

        # Evict from active table and push to output queue
        for key, flow in zip(expired_keys, expired_flows):
            self.flow_table.remove_flow(key)
            self.output_queue.push_nowait(flow)
            self.statistics.record_flow_expired()
            logger.debug(
                "Expired flow",
                flow_id=flow.flow_id,
                state=flow.state.value,
                duration=flow.duration_seconds,
            )

        if expired_flows:
            logger.info("Evicted expired flows", count=len(expired_flows), remaining_active=self.flow_table.active_count)

        return len(expired_flows)
