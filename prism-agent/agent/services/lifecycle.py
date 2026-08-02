"""Agent Daemon Startup and Shutdown Lifecycle Orchestrator with Resilient Auto-Registration and System Failover."""

import asyncio
import os
import sys
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
        """Sequential startup lifecycle with resilient registration and fault isolation."""
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
            registered = await self._resilient_registration_flow()
            if not registered:
                logger.warning("Initial server registration pending. Will continue retrying in background loop.")

        # 3. Start background telemetry Heartbeat Service
        await self.heartbeat_service.start()

        # 4. Start Real-Time Packet Capture Engine (if enabled)
        if agent_settings.CAPTURE_ENABLED:
            try:
                self.capture_engine.initialize()
                self.capture_engine.start()
                logger.info("Packet Capture Engine initialized and started successfully.")
            except Exception as exc:
                logger.warning(
                    "Packet Capture Engine unavailable (Npcap driver missing or interface permission restriction). Running in system telemetry mode.",
                    error=str(exc),
                )

        # 5. Start Flow Generation Engine (if enabled)
        if agent_settings.FLOW_ENABLED and agent_settings.CAPTURE_ENABLED:
            try:
                self.flow_engine.bind_packet_queue(self.capture_engine.queue)
                await self.flow_engine.start()
                logger.info("Flow Generation Engine initialized and started successfully.")
            except Exception as exc:
                logger.warning("Flow Generation Engine not active", error=str(exc))

        # 6. Start Advanced Feature Extraction Engine (if enabled)
        if agent_settings.FEATURE_EXTRACTION_ENABLED and agent_settings.FLOW_ENABLED and agent_settings.CAPTURE_ENABLED:
            try:
                self.feature_engine.bind_flow_queue(self.flow_engine.output_queue)
                await self.feature_engine.start()
                logger.info("Feature Extraction Engine initialized and started successfully.")
            except Exception as exc:
                logger.warning("Feature Extraction Engine not active", error=str(exc))

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
                logger.warning("Hybrid Intrusion Detection Engine not active", error=str(exc))

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
                logger.warning("Risk Engine not active", error=str(exc))

        # 9. Start persistent WebSocket Client
        await self.ws_client.start()

        logger.info("PRISM Agent daemon successfully initialized and running.")

    async def _resilient_registration_flow(self) -> bool:
        """Attempt registration with automatic interactive prompt or background retry loop."""
        attempts = 0
        max_quick_attempts = 2

        while attempts < max_quick_attempts:
            attempts += 1
            try:
                static_info = SystemCollector.collect_static_info()
                response = await self.http_client.post("/api/v1/agents/register", json_data=static_info)
                agent_id = response.get("agent_id")
                secret_key = response.get("secret_key")

                if agent_id and secret_key:
                    self.credentials_store.save_credentials(agent_id, secret_key)
                    self.http_client.set_credentials(agent_id, secret_key)
                    agent_state.agent_id = agent_id
                    agent_state.is_registered = True
                    agent_state.is_authenticated = True
                    logger.info("Agent registered successfully with PRISM Server", agent_id=agent_id)
                    return True
            except Exception as exc:
                logger.warning(
                    "Registration attempt failed",
                    attempt=attempts,
                    server_url=agent_settings.SERVER_URL,
                    error=str(exc),
                )
                await asyncio.sleep(1.0)

        # If interactive console is available, prompt user for Server URL
        if sys.stdin and sys.stdin.isatty():
            new_url = self._prompt_user_for_server_url()
            if new_url:
                agent_settings.update_server_url(new_url)
                logger.info("Updated Central Server URL", new_url=agent_settings.SERVER_URL)
                return await self._resilient_registration_flow()

        # Otherwise launch background reconnect task to keep retrying periodically
        asyncio.create_task(self._background_registration_retry_loop())
        return False

    def _prompt_user_for_server_url(self) -> Optional[str]:
        """Prompt user interactively for Central Admin Server URL on connection failure."""
        print("\n" + "=" * 68)
        print("🌐 PRISM Central Admin Server Connection Setup")
        print("=" * 68)
        print(f"Could not connect to PRISM Server at '{agent_settings.SERVER_URL}'.")
        print("Please enter the Central Admin Server URL (IP or Domain):")
        print("Example: http://192.168.1.50:8000 or http://prism-server:8000")
        print("-" * 68)
        try:
            user_input = input("Central Server URL: ").strip()
            if user_input:
                return user_input
        except Exception:
            pass
        return None

    async def _background_registration_retry_loop(self) -> None:
        """Periodically retry registration in background without crashing the daemon."""
        retry_delay = 10.0
        while not agent_state.is_registered:
            await asyncio.sleep(retry_delay)
            try:
                static_info = SystemCollector.collect_static_info()
                response = await self.http_client.post("/api/v1/agents/register", json_data=static_info)
                agent_id = response.get("agent_id")
                secret_key = response.get("secret_key")

                if agent_id and secret_key:
                    self.credentials_store.save_credentials(agent_id, secret_key)
                    self.http_client.set_credentials(agent_id, secret_key)
                    agent_state.agent_id = agent_id
                    agent_state.is_registered = True
                    agent_state.is_authenticated = True
                    logger.info("Background registration succeeded!", agent_id=agent_id)
                    break
            except Exception as exc:
                logger.debug("Background registration retry pending...", error=str(exc))
                retry_delay = min(60.0, retry_delay * 1.5)

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
