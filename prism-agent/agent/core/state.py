"""Agent Runtime State and Health Probe Tracker."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional


class AgentState:
    """Singleton tracking runtime connectivity, health status, and statistics."""

    def __init__(self) -> None:
        self.is_registered: bool = False
        self.is_authenticated: bool = False
        self.server_reachable: bool = False
        self.websocket_connected: bool = False
        self.last_heartbeat_sent: Optional[datetime] = None
        self.heartbeats_count: int = 0
        self.failed_heartbeats_count: int = 0
        self.agent_id: Optional[str] = None

    def mark_heartbeat_success(self) -> None:
        """Update state on successful heartbeat delivery."""
        self.last_heartbeat_sent = datetime.now(timezone.utc)
        self.heartbeats_count += 1
        self.server_reachable = True

    def mark_heartbeat_failed(self) -> None:
        """Update state on failed heartbeat delivery."""
        self.failed_heartbeats_count += 1
        self.server_reachable = False

    def get_health_status(self) -> Dict[str, Any]:
        """Compute local agent health overview."""
        overall_healthy = (
            self.is_registered
            and self.is_authenticated
            and self.server_reachable
        )

        return {
            "status": "healthy" if overall_healthy else "degraded",
            "registered": self.is_registered,
            "authenticated": self.is_authenticated,
            "server_reachable": self.server_reachable,
            "websocket_connected": self.websocket_connected,
            "agent_id": self.agent_id,
            "heartbeats_sent": self.heartbeats_count,
            "failed_heartbeats": self.failed_heartbeats_count,
            "last_heartbeat": self.last_heartbeat_sent.isoformat() if self.last_heartbeat_sent else None,
        }


agent_state = AgentState()
