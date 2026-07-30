# Network Interface Management Guide

The PRISM Agent automatically handles network interface selection across Linux and Windows environments.

## Interface Selection Precedence

1. Explicit configuration setting: `CAPTURE_INTERFACE="eth0"`
2. Default Scapy interface (`conf.iface`)
3. First active non-loopback network interface with valid IPv4 address
4. Fallback loopback or `eth0`
