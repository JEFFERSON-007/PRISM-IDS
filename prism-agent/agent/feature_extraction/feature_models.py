"""Feature Vector Data Model and Export Formatters."""

from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FeatureVector(BaseModel):
    """Standardized numerical feature vector representation of a completed flow."""

    # Flow Metadata
    flow_id: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    start_time: datetime
    end_time: datetime
    duration: float = Field(ge=0.0)

    # Packet Statistics
    total_packets: int = Field(ge=0)
    forward_packets: int = Field(ge=0)
    backward_packets: int = Field(ge=0)

    # Byte Statistics
    total_bytes: int = Field(ge=0)
    forward_bytes: int = Field(ge=0)
    backward_bytes: int = Field(ge=0)

    # Packet Length Statistics
    min_pkt_len: float = Field(ge=0.0)
    max_pkt_len: float = Field(ge=0.0)
    mean_pkt_len: float = Field(ge=0.0)
    std_pkt_len: float = Field(ge=0.0)
    variance_pkt_len: float = Field(ge=0.0)

    # Timing & Rate Features
    mean_iat: float = Field(ge=0.0)
    min_iat: float = Field(ge=0.0)
    max_iat: float = Field(ge=0.0)
    std_iat: float = Field(ge=0.0)
    packets_per_sec: float = Field(ge=0.0)
    bytes_per_sec: float = Field(ge=0.0)

    # TCP Features
    syn_count: int = Field(ge=0)
    ack_count: int = Field(ge=0)
    fin_count: int = Field(ge=0)
    rst_count: int = Field(ge=0)
    psh_count: int = Field(ge=0)
    urg_count: int = Field(ge=0)
    syn_ratio: float = Field(ge=0.0, le=1.0)
    ack_ratio: float = Field(ge=0.0, le=1.0)

    # Flow Ratios
    fwd_bwd_packet_ratio: float = Field(ge=0.0)
    fwd_bwd_byte_ratio: float = Field(ge=0.0)
    avg_bytes_per_pkt: float = Field(ge=0.0)

    # Protocol Features
    service_name: str = Field(default="UNKNOWN")
    is_encrypted: bool = False

    # Entropy Features
    pkt_size_entropy: float = Field(ge=0.0)
    direction_entropy: float = Field(ge=0.0)

    # Behavioral Indicators
    is_long_flow: bool = False
    is_burst_traffic: bool = False
    is_large_transfer: bool = False
    is_high_pkt_rate: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert FeatureVector to dictionary."""
        return self.model_dump(mode="json")

    def to_json(self) -> str:
        """Serialize FeatureVector to JSON string."""
        return self.model_dump_json()

    def to_numpy_list(self) -> List[float]:
        """Convert key numerical features to an ordered float array for ML input."""
        return [
            float(self.duration),
            float(self.total_packets),
            float(self.forward_packets),
            float(self.backward_packets),
            float(self.total_bytes),
            float(self.forward_bytes),
            float(self.backward_bytes),
            float(self.min_pkt_len),
            float(self.max_pkt_len),
            float(self.mean_pkt_len),
            float(self.std_pkt_len),
            float(self.variance_pkt_len),
            float(self.mean_iat),
            float(self.min_iat),
            float(self.max_iat),
            float(self.std_iat),
            float(self.packets_per_sec),
            float(self.bytes_per_sec),
            float(self.syn_count),
            float(self.ack_count),
            float(self.fin_count),
            float(self.rst_count),
            float(self.syn_ratio),
            float(self.ack_ratio),
            float(self.fwd_bwd_packet_ratio),
            float(self.fwd_bwd_byte_ratio),
            float(self.avg_bytes_per_pkt),
            float(self.pkt_size_entropy),
            float(self.direction_entropy),
        ]
