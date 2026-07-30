"""Network Interface Discovery, Selection, and Health Management."""

import platform
from typing import Dict, List, Optional, Any
import psutil
from scapy.arch import get_if_list
from scapy.config import conf
import structlog
from agent.core.config import agent_settings

logger = structlog.get_logger("prism_agent.interface_manager")


class InterfaceManager:
    """Manages detection, validation, and selection of network interfaces for packet sniffing."""

    @staticmethod
    def list_interfaces() -> List[Dict[str, Any]]:
        """List all available system network interfaces with IP/MAC metadata."""
        interfaces: List[Dict[str, Any]] = []
        net_addrs = psutil.net_if_addrs()
        net_stats = psutil.net_if_stats()

        for iface_name, addrs in net_addrs.items():
            ip_addr = None
            mac_addr = None
            for addr in addrs:
                if addr.family == 2:  # AF_INET (IPv4)
                    ip_addr = addr.address
                elif addr.family in (-1, 17, 18):  # MAC address family across OSes
                    mac_addr = addr.address

            stats = net_stats.get(iface_name)
            is_up = stats.isup if stats else True
            mtu = stats.mtu if stats else 1500

            interfaces.append({
                "name": iface_name,
                "ip_address": ip_addr or "N/A",
                "mac_address": mac_addr or "N/A",
                "is_up": is_up,
                "mtu": mtu,
                "is_loopback": iface_name.lower().startswith("lo") or ip_addr == "127.0.0.1",
            })

        return interfaces

    @classmethod
    def select_best_interface(cls, preferred: Optional[str] = None) -> str:
        """Select preferred interface or auto-select active non-loopback interface."""
        available_ifaces = get_if_list()
        logger.debug("Scapy available interfaces", ifaces=available_ifaces)

        if preferred and (preferred in available_ifaces or preferred in [i["name"] for i in cls.list_interfaces()]):
            logger.info("Selected user-specified capture interface", interface=preferred)
            return preferred

        # Default fallback via Scapy conf.iface
        scapy_default = conf.iface
        if scapy_default and str(scapy_default) in available_ifaces:
            logger.info("Selected default Scapy interface", interface=str(scapy_default))
            return str(scapy_default)

        # Fallback to first non-loopback active interface
        for iface in cls.list_interfaces():
            if iface["is_up"] and not iface["is_loopback"]:
                logger.info("Auto-selected non-loopback active interface", interface=iface["name"])
                return iface["name"]

        # Last resort fallback
        fallback = available_ifaces[0] if available_ifaces else "eth0"
        logger.warning("Fallback interface selected", interface=fallback)
        return fallback

    @classmethod
    def validate_interface(cls, iface_name: str) -> bool:
        """Verify if target interface is available and readable."""
        ifaces = [i["name"] for i in cls.list_interfaces()] + get_if_list()
        return iface_name in ifaces
