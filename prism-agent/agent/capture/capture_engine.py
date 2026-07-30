"""Master Packet Capture Engine Lifecycle Controller."""

from typing import Any, Dict, Optional
from scapy.packet import Packet
import structlog
from agent.capture.capture_filters import BPFBuilder
from agent.capture.capture_statistics import CaptureStatistics
from agent.capture.interface_manager import InterfaceManager
from agent.capture.packet_listener import PacketListener
from agent.capture.packet_parser import PacketParser
from agent.capture.packet_queue import PacketQueue
from agent.core.config import agent_settings

logger = structlog.get_logger("prism_agent.capture_engine")


class CaptureEngine:
    """High-level Packet Capture Engine managing acquisition, parsing, queueing, and metrics."""

    def __init__(self) -> None:
        self.interface: Optional[str] = None
        self.bpf_filter: str = agent_settings.BPF_FILTER
        self.queue = PacketQueue(maxsize=agent_settings.QUEUE_MAX_SIZE)
        self.statistics = CaptureStatistics()
        self.listener: Optional[PacketListener] = None
        self._paused: bool = False
        self._is_initialized: bool = False

    def initialize(self, interface: Optional[str] = None, bpf_filter: Optional[str] = None) -> None:
        """Initialize interface and validate BPF filter string."""
        target_iface = interface or agent_settings.CAPTURE_INTERFACE
        self.interface = InterfaceManager.select_best_interface(preferred=target_iface)

        if bpf_filter:
            if BPFBuilder.validate_bpf(bpf_filter):
                self.bpf_filter = bpf_filter
            else:
                logger.warning("Invalid BPF filter provided; reverting to default", invalid_filter=bpf_filter)

        self._is_initialized = True
        logger.info(
            "Packet Capture Engine initialized",
            interface=self.interface,
            bpf_filter=self.bpf_filter,
            queue_max_size=self.queue.maxsize,
        )

    def start(self) -> None:
        """Start packet acquisition."""
        if not self._is_initialized:
            self.initialize()

        if self.listener and self.listener.is_running:
            logger.warning("Capture Engine is already running")
            return

        self.statistics.start()
        self._paused = False

        self.listener = PacketListener(
            interface=self.interface,
            bpf_filter=self.bpf_filter,
            packet_callback=self._handle_raw_packet,
            promiscuous=agent_settings.PROMISCUOUS_MODE,
            packet_limit=agent_settings.PACKET_LIMIT,
        )
        self.listener.start()
        logger.info("Packet Capture Engine started successfully", interface=self.interface)

    def pause(self) -> None:
        """Pause packet queueing while listener thread runs."""
        self._paused = True
        logger.info("Packet Capture Engine paused")

    def resume(self) -> None:
        """Resume packet queueing."""
        self._paused = False
        logger.info("Packet Capture Engine resumed")

    def stop(self) -> None:
        """Stop packet acquisition."""
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.statistics.stop()
        logger.info("Packet Capture Engine stopped")

    def _handle_raw_packet(self, scapy_pkt: Packet) -> None:
        """Callback invoked by Scapy thread for each captured packet."""
        if self._paused:
            return

        try:
            raw_len = len(scapy_pkt)
            self.statistics.record_packet(raw_len)

            parsed_pkt = PacketParser.parse(scapy_pkt)
            if parsed_pkt:
                pushed = self.queue.push_nowait(parsed_pkt)
                if not pushed:
                    self.statistics.record_drop()
            else:
                self.statistics.record_error()
        except Exception as exc:
            self.statistics.record_error()
            logger.error("Error processing captured packet", error=str(exc))

    def get_status(self) -> Dict[str, Any]:
        """Return runtime state and performance statistics snapshot."""
        return {
            "initialized": self._is_initialized,
            "running": self.listener.is_running if self.listener else False,
            "paused": self._paused,
            "interface": self.interface,
            "bpf_filter": self.bpf_filter,
            "queue_size": self.queue.size,
            "queue_max_size": self.queue.maxsize,
            "statistics": self.statistics.get_summary(),
        }
