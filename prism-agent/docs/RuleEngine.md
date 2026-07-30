# Signature Rule Engine Specification

The Signature Engine evaluates JSON-formatted rules defined in `rules/signature_rules.json`.

## Rule Format Example

```json
{
  "rule_id": "SIG-002",
  "name": "TCP SYN Flood Indicator",
  "description": "High proportion of SYN packets with low ACK responses",
  "severity": "CRITICAL",
  "protocol": "TCP",
  "enabled": true,
  "conditions": {
    "min_syn_ratio": 0.8,
    "max_ack_ratio": 0.2,
    "min_packets": 10
  },
  "action": "ALERT"
}
```
