# Severity Classification Thresholds

| Severity Level | Risk Score Range | Description |
|---|---|---|
| `INFORMATIONAL` | $0.0 \le R < 20.0$ | Low-risk network telemetry / non-malicious anomalies |
| `LOW` | $20.0 \le R < 40.0$ | Suspicious protocol activity without active exploit |
| `MEDIUM` | $40.0 \le R < 70.0$ | High-frequency connection bursts / brute force attempts |
| `HIGH` | $70.0 \le R < 90.0$ | Confirmed port scans / SYN floods / suspicious traffic |
| `CRITICAL` | $90.0 \le R \le 100.0$ | Multi-vector attacks / hybrid agreement / sensitive port attacks |
