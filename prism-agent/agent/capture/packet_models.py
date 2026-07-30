"""Packet Data Models for Parsed Network Telemetry."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid
from pydantic import BaseModel, Field


class PacketProtocol(str, Enum):
    """Network transport layer protocols."""

    TCP = "TCP"
    UDP = "UDP"
    ICMP = "ICMP"
    ARP = "ARP"
    OTHER = "OTHER"


class EthernetHeader(BaseModel):
    """Ethernet Data Link layer header details."""

    src_mac: str = Field(default="00:00:00:00:00:00", description="Source MAC Address")
    dst_mac: str = Field(default="00:00:00:00:00:00", description="Destination MAC Address")
    ethertype: int = Field(default=0x0800, description="Ethernet Type Code (e.g. 0x0800 for IPv4)")


class IPHeader(BaseModel):
    """IPv4/IPv6 Network layer header details."""

    src_ip: str = Field(description="Source IP Address")
    dst_ip: str = Field(description="Destination IP Address")
    version: int = Field(description="IP Version (4 or 6)")
    ttl: int = Field(description="Time to Live / Hop Limit")
    protocol_number: int = Field(description="IP Protocol Number (6=TCP, 17=UDP, 1=ICMP)")
    length: int = Field(default=0, description="Total Packet Length in bytes")
    id: Optional[int] = Field(default=None, description="IP Identification Field")


class TCPFlags(BaseModel):
    """TCP Control Flags."""

    syn: bool = False
    ack: bool = False
    fin: bool = False
    rst: bool = False
    psh: bool = False
    urg: bool = False


class TCPHeader(BaseModel):
    """TCP Transport layer header details."""

    src_port: int = Field(ge=0, le=65535)
    dst_port: int = Field(ge=0, le=65535)
    seq: int = Field(description="Sequence Number")
    ack: Optional[int] = Field(default=None, description="Acknowledgment Number")
    flags: TCPFlags
    window: int = Field(description="TCP Window Size")


class UDPHeader(BaseModel):
    """UDP Transport layer header details."""

    src_port: int = Field(ge=0, le=65535)
    dst_port: int = Field(ge=0, le=65535)
    length: int = Field(default=0, description="UDP Datagram Length")


class ICMPHeader(BaseModel):
    """ICMP Control Message details."""

    type: int = Field(description="ICMP Message Type")
    code: int = Field(description="ICMP Message Code")


class ParsedPacket(BaseModel):
    """Unified strongly typed representation of a captured network packet."""

    packet_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_length: int = Field(description="Raw packet size in bytes")
    protocol: PacketProtocol = Field(description="Identified protocol")

    eth_header: Optional[EthernetHeader] = None
    ip_header: Optional[IPHeader] = None
    tcp_header: Optional[TCPHeader] = None
    udp_header: Optional[UDPHeader] = None
    icmp_header: Optional[ICMPHeader] = None

    payload_length: int = 0
    payload_snippet: Optional[str] = Field(default=None, description="Hex/ASCII snippet of payload for inspection")
