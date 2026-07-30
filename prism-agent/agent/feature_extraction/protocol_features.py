"""Protocol and Application Service Feature Extractor."""

from typing import Dict, Any
from agent.flow.flow_models import Flow

WELL_KNOWN_PORTS = {
    80: "HTTP",
    443: "HTTPS",
    53: "DNS",
    22: "SSH",
    21: "FTP",
    25: "SMTP",
    587: "SMTP",
    3389: "RDP",
    1883: "MQTT",
    8080: "HTTP_ALT",
}


class ProtocolFeatures:
    """Extracts network protocol numbers, application service tags, and encryption hints."""

    @staticmethod
    def extract(flow: Flow) -> Dict[str, Any]:
        """Map ports to well-known service names and encryption indicators."""
        src_port, dst_port = flow.src_port, flow.dst_port
        service = WELL_KNOWN_PORTS.get(dst_port) or WELL_KNOWN_PORTS.get(src_port) or "UNKNOWN"

        is_encrypted = (dst_port == 443 or src_port == 443 or service in ("HTTPS", "SSH"))

        return {
            "service_name": service,
            "is_encrypted": is_encrypted,
        }
