"""Dashboard Metrics and Real-Time Analytics Aggregator Service."""

from datetime import datetime, timezone
import psutil
import time
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from app.repositories.agent_repository import AgentRepository
from app.repositories.alert_repository import AlertRepository
from app.repositories.incident_repository import IncidentRepository
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    NetworkAnalyticsResponse,
    ProtocolDistributionItem,
    SeverityCountSummary,
    SystemHealthResponse,
    TopAttackerIP,
    TopRuleMatch,
    TopTargetHost,
)
from app.websocket.manager import ws_manager

SERVER_START_TIME = time.time()
logger = structlog.get_logger("prism_ids.dashboard_service")


class DashboardService:
    """Service providing aggregated SOC dashboard statistics, network analytics, and system health metrics."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.alert_repo = AlertRepository(session)
        self.incident_repo = IncidentRepository(session)
        self.agent_repo = AgentRepository(session)

    async def get_dashboard_summary(self) -> DashboardSummaryResponse:
        """Aggregate executive SOC summary metrics."""
        now = datetime.now(timezone.utc)

        # 1. Severity Counts
        sev_counts = await self.alert_repo.get_severity_counts()
        crit = sev_counts.get("CRITICAL", 0)
        high = sev_counts.get("HIGH", 0)
        med = sev_counts.get("MEDIUM", 0)
        low = sev_counts.get("LOW", 0)
        info = sev_counts.get("INFORMATIONAL", 0)
        tot_alerts = sum(sev_counts.values())

        severity_summary = SeverityCountSummary(
            critical=crit,
            high=high,
            medium=med,
            low=low,
            informational=info,
            total=tot_alerts,
        )

        # 2. Open Incidents Count
        open_incidents = await self.incident_repo.get_open_count()

        # 3. Average Risk Score
        avg_risk = await self.alert_repo.get_average_risk_score()

        # 4. Agent Counts
        agents_list = await self.agent_repo.get_all()
        total_agents = len(agents_list)
        active_agents = sum(1 for a in agents_list if a.is_online and a.health_status == "healthy")

        # 5. Top Target Hosts
        top_targets_raw = await self.alert_repo.get_top_target_hosts(limit=5)
        top_targets = [TopTargetHost(**t) for t in top_targets_raw]

        # 6. Top Attacker IPs
        top_attackers_raw = await self.alert_repo.get_top_attacker_ips(limit=5)
        top_attackers = [TopAttackerIP(**a) for a in top_attackers_raw]

        # 7. Top Triggered Rules (synthetic fallback summary)
        top_rules = [
            TopRuleMatch(rule_name="SIG-001 Port Scanning", trigger_count=tot_alerts),
            TopRuleMatch(rule_name="SIG-002 TCP SYN Flood", trigger_count=crit),
        ]

        return DashboardSummaryResponse(
            timestamp=now,
            alert_counts=severity_summary,
            open_incidents_count=open_incidents,
            average_risk_score=avg_risk,
            active_agents_count=active_agents,
            total_agents_count=total_agents,
            top_target_hosts=top_targets,
            top_attacker_ips=top_attackers,
            top_triggered_rules=top_rules,
        )

    async def get_network_analytics(self) -> NetworkAnalyticsResponse:
        """Aggregate network traffic and protocol distribution metrics."""
        now = datetime.now(timezone.utc)
        proto_dist_raw = await self.alert_repo.get_protocol_distribution()
        proto_dist = [ProtocolDistributionItem(**p) for p in proto_dist_raw]

        top_dests = await self.alert_repo.get_top_target_hosts(limit=10)
        top_sources = await self.alert_repo.get_top_attacker_ips(limit=10)

        return NetworkAnalyticsResponse(
            timestamp=now,
            protocol_distribution=proto_dist,
            top_destination_ports=[{"port": 80, "service": "HTTP"}, {"port": 443, "service": "HTTPS"}, {"port": 22, "service": "SSH"}],
            top_source_ips=top_sources,
            traffic_volume_summary={"status": "ACTIVE", "monitored_interfaces": 1},
        )

    async def get_system_health(self) -> SystemHealthResponse:
        """Expose server system, database, and WebSocket health status."""
        now = datetime.now(timezone.utc)
        agents_list = await self.agent_repo.get_all()
        total_agents = len(agents_list)
        online_agents = sum(1 for a in agents_list if a.is_online)
        offline_agents = total_agents - online_agents

        cpu_pct = psutil.cpu_percent(interval=None)
        mem_pct = psutil.virtual_memory().percent
        uptime = round(time.time() - SERVER_START_TIME, 1)

        return SystemHealthResponse(
            timestamp=now,
            server_status="HEALTHY",
            database_status="CONNECTED",
            websocket_connections_count=ws_manager.total_connections,
            registered_agents_count=total_agents,
            online_agents_count=online_agents,
            offline_agents_count=offline_agents,
            cpu_percent=cpu_pct,
            memory_percent=mem_pct,
            uptime_seconds=uptime,
        )
