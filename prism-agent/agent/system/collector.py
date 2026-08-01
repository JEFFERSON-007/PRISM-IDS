"""System Hardware and OS Telemetry Collector using Platform and Psutil."""

from datetime import datetime, timezone
import platform
import socket
from typing import Any, Dict
import psutil
import structlog
from agent.core.config import agent_settings

logger = structlog.get_logger("prism_agent.collector")


class SystemCollector:
    """Collects node hardware, operating system, and network interface metrics."""

    @staticmethod
    def get_primary_ip() -> str:
        """Attempt to determine primary IPv4 address."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"

    @staticmethod
    def collect_static_info() -> Dict[str, Any]:
        """Collect host system metadata for agent registration."""
        hostname = socket.gethostname()
        ip_addr = SystemCollector.get_primary_ip()
        os_info = f"{platform.system()} {platform.release()}"

        # If agent_name is default placeholder, dynamically format with machine hostname
        agent_name = agent_settings.AGENT_NAME
        if agent_name in ["agent-node-01", "remote-agent-sensor"]:
            agent_name = f"agent-{hostname.lower()}"

        return {
            "agent_name": agent_name,
            "hostname": hostname,
            "ip_address": ip_addr,
            "operating_system": os_info,
            "version": agent_settings.AGENT_VERSION,
            "kernel_version": platform.version(),
            "python_version": platform.python_version(),
            "cpu_cores": psutil.cpu_count(logical=True),
            "ram_total_bytes": psutil.virtual_memory().total,
        }

    @staticmethod
    def collect_telemetry() -> Dict[str, Any]:
        """Collect periodic resource utilization metrics for heartbeat transmission."""
        cpu_usage = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu_usage": round(cpu_usage, 2),
            "ram_usage": round(mem.percent, 2),
            "disk_usage": round(disk.percent, 2),
            "network_status": "ok",
            "agent_version": agent_settings.AGENT_VERSION,
        }
