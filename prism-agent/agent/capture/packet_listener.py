"""Background Scapy Packet Sniffing Listener Thread."""

import threading
from typing import Callable, Optional
from scapy.all import sniff
from scapy.packet import Packet
import structlog
from agent.core.config import agent_settings

logger = structlog.get_logger("prism_agent.packet_listener")


class PacketListener:
    """Runs a Scapy sniff session in a background daemon thread."""

    def __init__(
        self,
        interface: str,
        bpf_filter: str = "ip or ip6",
        packet_callback: Optional[Callable[[Packet], None]] = None,
        promiscuous: bool = True,
        packet_limit: int = 0,
    ) -> None:
        self.interface = interface
        self.bpf_filter = bpf_filter
        self.packet_callback = packet_callback
        self.promiscuous = promiscuous
        self.packet_limit = packet_limit

        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._is_running = False

    @property
    def is_running(self) -> bool:
        """Return listener execution state."""
        return self._is_running

    def start(self) -> None:
        """Start packet sniffing in background thread."""
        if self._is_running:
            return

        self._stop_event.clear()
        self._is_running = True
        self._thread = threading.Thread(target=self._sniff_loop, daemon=True, name="ScapySnifferThread")
        self._thread.start()
        logger.info(
            "Background packet listener thread started",
            interface=self.interface,
            bpf_filter=self.bpf_filter,
            promiscuous=self.promiscuous,
        )

    def stop(self) -> None:
        """Stop packet sniffing loop."""
        if not self._is_running:
            return

        self._stop_event.set()
        self._is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        logger.info("Background packet listener thread stopped")

    def _sniff_loop(self) -> None:
        """Internal sniffing loop delegating packets to callback."""

        def stop_check(pkt: Packet) -> bool:
            return self._stop_event.is_set()

        def internal_prn(pkt: Packet) -> None:
            if self.packet_callback:
                try:
                    self.packet_callback(pkt)
                except Exception as exc:
                    logger.error("Error in packet listener callback", error=str(exc))

        try:
            sniff(
                iface=self.interface,
                filter=self.bpf_filter,
                prn=internal_prn,
                stop_filter=stop_check,
                store=0,
                count=self.packet_limit if self.packet_limit > 0 else 0,
            )
        except Exception as exc:
            logger.error("Scapy sniffing session encountered error", error=str(exc))
        finally:
            self._is_running = False
