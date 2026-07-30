# Packet Capture Engine Architecture

## Subsystem Architecture

The **Packet Capture Engine** captures live network frames from host interfaces, parses protocol headers, and buffers structured packet DTOs for downstream consumption.

```
┌────────────────────────────────────────────────────────────┐
│                    Interface Manager                       │
│             (Selects active capture interface)             │
└─────────────────────────────┬──────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                    BPF Filter Builder                      │
│            (Constrains sniffing scope e.g. ip)             │
└─────────────────────────────┬──────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                     Scapy Sniffer Thread                   │
│         (Captures raw link layer frames safely)            │
└─────────────────────────────┬──────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                     Packet Parser                          │
│     (Extracts Ethernet, IP, TCP, UDP, ICMP headers)        │
└─────────────────────────────┬──────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                  Bounded Async Packet Queue                │
│       (Buffers ParsedPacket DTOs with overflow drops)      │
└────────────────────────────────────────────────────────────┘
```

---

## 1. Interface Auto-Detection (`interface_manager.py`)
- Discovers available interfaces using `psutil` and Scapy.
- Selects specified interface or falls back to active non-loopback interface.

## 2. BPF Filter Support (`capture_filters.py`)
- Validates and constructs Berkeley Packet Filters (e.g. `tcp`, `udp`, `port 80`, `host 192.168.1.1`).

## 3. Packet Parser & Validation (`packet_parser.py` & `packet_validator.py`)
- Extracts timestamps, raw sizes, IP version, source/destination IPs, ports, TTL, protocol numbers, TCP flags (SYN, ACK, FIN, RST, PSH, URG), MAC addresses, and payload snippets.

## 4. Packet Queue (`packet_queue.py`)
- Bounded async ring buffer (`maxsize=10000`). Drops oldest packets under burst traffic to maintain low memory consumption.

## 5. Live Capture Statistics (`capture_statistics.py`)
- Maintains live throughput counters (`packets_captured`, `packets_dropped`, `bytes_captured`, `packets_per_second`).
