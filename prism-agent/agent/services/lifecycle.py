"""Agent Daemon Startup and Shutdown Lifecycle Orchestrator."""

import asyncio
from typing import Optional
import structlog
from agent.authentication.credentials_store import CredentialsStore
from agent.capture.capture_engine import CaptureEngine
from agent.communication.http_client import AgentHTTPClient
from agent.communication.websocket_client import AgentWebSocketClient
from agent.core.config import agent_settings
from agent.core.logging import setup_agent_logging
from agent.core.state import agent_state
from agent.detection.hybrid_engine import HybridEngine
from agent.feature_extraction.feature_engine import FeatureEngine
from agent.flow.flow_engine import FlowEngine
from agent.heartbeat.service import HeartbeatDaemonService
from agent.risk.risk_engine import RiskEngine
from agent.system.collector import SystemCollector

logger = structlog.get_logger("prism_agent.lifecycle")


class AgentLifecycleManager:
    """Orchestrates initialization, onboarding, daemon loops, packet capture, flow generation, feature extraction, hybrid detection, risk scoring, and graceful shutdown."""

    def __init__(self) -> None:
        self.credentials_store = CredentialsStore()
        self.http_client = AgentHTTPClient()
        self.ws_client = AgentWebSocketClient()
        self.heartbeat_service = HeartbeatDaemonService(http_client=self.http_client)
        self.capture_engine = CaptureEngine()
        self.flow_engine = FlowEngine()
        self.feature_engine = FeatureEngine()
        self.detection_engine = HybridEngine()
        self.risk_engine = RiskEngine(http_client=self.http_client)
        self._shutdown_event = asyncio.Event()

    async def initialize_and_start(self) -> None:
        """Sequential startup lifecycle."""
        # 1. Setup Logging
        setup_agent_logging()
        logger.info(
            "Starting PRISM IDS Agent Daemon",
            agent_name=agent_settings.AGENT_NAME,
            version=agent_settings.AGENT_VERSION,
            server_url=agent_settings.SERVER_URL,
        )

        # 2. Check local credentials or register with PRISM Server
        creds = self.credentials_store.load_credentials()
        if creds:
            logger.info("Found existing local agent credentials", agent_id=creds["agent_id"])
            self.http_client.set_credentials(creds["agent_id"], creds["secret_key"])
            agent_state.agent_id = creds["agent_id"]
            agent_state.is_registered = True
            agent_state.is_authenticated = True
        else:
            logger.info("No credentials found. Initiating registration with PRISM Server...")
            await self._register_with_server()

        # 3. Start background telemetry Heartbeat Service
        await self.heartbeat_service.start()

        # 4. Start Real-Time Packet Capture Engine (if enabled)
        if agent_settings.CAPTURE_ENABLED:
            try:
                self.capture_engine.initialize()
                self.capture_engine.start()
                logger.info("Packet Capture Engine initialized and started successfully.")
            except Exception as exc:
                logger.error("Failed to start Packet Capture Engine", error=str(exc))

        # 5. Start Flow Generation Engine (if enabled)
        if agent_settings.FLOW_ENABLED and agent_settings.CAPTURE_ENABLED:
            try:
                self.flow_engine.bind_packet_queue(self.capture_engine.queue)
                await self.flow_engine.start()
                logger.info("Flow Generation Engine initialized and started successfully.")
            except Exception as exc:
                logger.error("Failed to start Flow Generation Engine", error=str(exc))

        # 6. Start Advanced Feature Extraction Engine (if enabled)
        if agent_settings.FEATURE_EXTRACTION_ENABLED and agent_settings.FLOW_ENABLED and agent_settings.CAPTURE_ENABLED:
            try:
                self.feature_engine.bind_flow_queue(self.flow_engine.output_queue)
                await self.feature_engine.start()
                logger.info("Feature Extraction Engine initialized and started successfully.")
            except Exception as exc:
                logger.error("Failed to start Feature Extraction Engine", error=str(exc))

        # 7. Start Hybrid Intrusion Detection Engine (if enabled)
        if (
            agent_settings.DETECTION_ENABLED
            and agent_settings.FEATURE_EXTRACTION_ENABLED
            and agent_settings.FLOW_ENABLED
            and agent_settings.CAPTURE_ENABLED
        ):
            try:
                self.detection_engine.bind_feature_queue(self.feature_engine.output_queue)
                await self.detection_engine.start()
                logger.info("Hybrid Intrusion Detection Engine initialized and started successfully.")
            except Exception as exc:
                logger.error("Failed to start Hybrid Intrusion Detection Engine", error=str(exc))

        # 8. Start Risk Engine & Alert Management System (if enabled)
        if (
            agent_settings.RISK_ENGINE_ENABLED
            and agent_settings.DETECTION_ENABLED
            and agent_settings.FEATURE_EXTRACTION_ENABLED
            and agent_settings.FLOW_ENABLED
            and agent_settings.CAPTURE_ENABLED
        ):
            try:
                self.risk_engine.set_http_client(self.http_client)
                self.risk_engine.bind_detection_queue(self.detection_engine.output_queue)
                await self.risk_engine.start()
                logger.info("Risk Engine and Alert Management System initialized and started successfully.")
            except Exception as exc:
                logger.error("Failed to start Risk Engine and Alert Management System", error=str(exc))

        # 9. Start persistent WebSocket Client
        await self.ws_client.start()

        logger.info("PRISM Agent daemon successfully initialized and running.")

    async def _register_with_server(self) -> None:
        """Register agent with PRISM Server and save issued credentials."""
        static_info = SystemCollector.collect_static_info()
        try:
            response = await self.http_client.post("/api/v1/agents/register", json_data=static_info)
            agent_id = response.get("agent_id")
            secret_key = response.get("secret_key")

            if not agent_id or not secret_key:
                raise RuntimeError("Invalid registration response payload from server")

            self.credentials_store.save_credentials(agent_id, secret_key)
            self.http_client.set_credentials(agent_id, secret_key)
            agent_state.agent_id = agent_id
            agent_state.is_registered = True
            agent_state.is_authenticated = True

            logger.info("Agent registered successfully with PRISM Server", agent_id=agent_id)
        except Exception as exc:
            logger.critical("Agent registration failed", error=str(exc))
            raise

    async def shutdown(self) -> None:
        """Clean shutdown of daemon services, risk engine, detection engine, feature engine, flow engine, and packet capture."""
        logger.info("Initiating graceful shutdown of PRISM Agent...")
        if agent_settings.RISK_ENGINE_ENABLED:
            await self.risk_engine.stop()

        if agent_settings.DETECTION_ENABLED:
            await self.detection_engine.stop()

        if agent_settings.FEATURE_EXTRACTION_ENABLED:
            await self.feature_engine.stop()

        if agent_settings.FLOW_ENABLED:
            await self.flow_engine.stop()

        if agent_settings.CAPTURE_ENABLED:
            self.capture_engine.stop()

        await self.heartbeat_service.stop()
        await self.ws_client.stop()
        logger.info("PRISM Agent shutdown complete.")
