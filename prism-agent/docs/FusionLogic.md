# Detection Fusion and Confidence Scoring

## Fusion Decision Matrix

| Signature Match | ML Malicious | Detection Method | Resulting Severity |
|---|---|---|---|
| No | No | N/A | Discarded (Benign) |
| Yes | No | `SIGNATURE` | Rule Severity |
| No | Yes | `MACHINE_LEARNING` | ML Probability Mapping |
| Yes | Yes | `HYBRID` | Elevated Severity (e.g. CRITICAL) |

## Confidence Calculation

$$C = \min\left(1.0, w_{\text{sig}} S_{\text{sig}} + w_{\text{ml}} P_{\text{ml}} + \text{Bonus}\right)$$
