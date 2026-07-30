# Risk Engine Architecture

The **Risk Engine** converts raw `DetectionResult` objects into normalized numerical risk scores ($0.0 - 100.0$) and maps them to standard security severity tiers.

```
┌────────────────────────────────────────────────────────────┐
│              Hybrid Detection Output Queue                 │
│               (Pushes DetectionResult DTOs)                │
└─────────────────────────────┬──────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                    Risk Calculator                         │
│ (Weights Severity + ML Confidence + Port Bonus + Frequency)│
└─────────────────────────────┬──────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                   Severity Classifier                      │
│     (Maps Risk Score 0-100 to INFO, LOW, MED, HIGH, CRIT)  │
└─────────────────────────────┬──────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                  Sliding Deduplicator                      │
│     (Suppresses duplicate alerts within 60s window)        │
└─────────────────────────────┬──────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                    Alert Correlator                        │
│     (Assigns correlation_id to multi-target scans)         │
└─────────────────────────────┬──────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                   Alert Sender Daemon                      │
│ (Transmits Alert DTO to Server with exponential backoff)   │
└────────────────────────────────────────────────────────────┘
```

---

## Normalized Risk Score Formula

$$R = \min\left(100.0, \Big(S_{\text{base}} \cdot \text{Conf} + P_{\text{bonus}}\Big) \cdot \Big(1 + 0.2 \cdot \log_{10}(N_{\text{occurrences}})\Big)\right)$$

Where:
- $S_{\text{base}}$: Base severity score ($\text{LOW}=25, \text{MEDIUM}=50, \text{HIGH}=75, \text{CRITICAL}=95$).
- $\text{Conf}$: Detection confidence probability ($0.5 - 1.0$).
- $P_{\text{bonus}}$: Sensitive port bonus ($\text{SSH}: 15, \text{RDP}: 15, \text{Postgres}: 10$).
- $N_{\text{occurrences}}$: Deduplicated occurrence frequency counter.
