"""Background Heartbeat Telemetry Daemon Service."""

import asyncio
from typing import Optional
import structlog
from agent.communication.http_client import AgentHTTPClient
from agent.core.config import agent_settings
from agent.core.state import agent_state
from agent.system.collector import SystemCollector

logger = structlog.get_logger("prism_agent.heartbeat_service")


class HeartbeatDaemonService:
    """Daemon running background telemetry heartbeat loop."""

    def __init__(self, http_client: AgentHTTPClient) -> None:
        self.http_client = http_client
        self._running: bool = False
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the background heartbeat transmission loop."""
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info(
            "Heartbeat background service started", interval_seconds=agent_settings.HEARTBEAT_INTERVAL
        )

    async def stop(self) -> None:
        """Stop the background heartbeat transmission loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped heartbeat background service")

    async def _run_loop(self) -> None:
        """Continuous heartbeat execution loop."""
        while self._running:
            try:
                telemetry = SystemCollector.collect_telemetry()
                response = await self.http_client.post("/api/v1/agents/heartbeat", json_data=telemetry)
                agent_state.mark_heartbeat_success()
                logger.debug(
                    "Transmitted heartbeat telemetry",
                    cpu_usage=telemetry["cpu_usage"],
                    ram_usage=telemetry["ram_usage"],
                )
            except Exception as exc:
                agent_state.mark_heartbeat_failed()
                logger.error("Failed to transmit heartbeat telemetry", error=str(exc))

            try:
                await asyncio.sleep(agent_settings.HEARTBEAT_INTERVAL)
            except asyncio.CancelledError:
                break
