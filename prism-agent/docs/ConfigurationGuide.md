# Packet Capture Engine Configuration Guide

Add the following environment variables to `.env.agent` to configure packet capture:

```env
# Packet Capture Parameters
CAPTURE_ENABLED=true
CAPTURE_INTERFACE="eth0"
BPF_FILTER="ip or ip6"
PROMISCUOUS_MODE=true
BUFFER_SIZE=1048576
QUEUE_MAX_SIZE=10000
PACKET_LIMIT=0
CAPTURE_BACKEND="scapy"
```
