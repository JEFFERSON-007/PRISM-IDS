# Advanced Feature Extraction Engine Architecture

The **Feature Extraction Engine** converts completed network flow records (`Flow`) into standardized numerical `FeatureVector` DTOs for downstream detection modules.

```
┌────────────────────────────────────────────────────────────┐
│                    Flow Engine Output Queue                │
│                 (Pushes completed Flow objects)            │
└─────────────────────────────┬──────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                    Feature Pipeline                        │
│ (Calculates Statistical, Timing, TCP, Protocol & Entropy)  │
└─────────────────────────────┬──────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                    Feature Validator                       │
│    (Checks for NaN, Inf, negative values & sanitizes)      │
└─────────────────────────────┬──────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                  Bounded Output Feature Queue              │
│  (Buffers FeatureVectors for Signature & ML engines)       │
└────────────────────────────────────────────────────────────┘
```

---

## Subsystem Modules

1. **`statistical_features.py`**: Min, max, mean, standard deviation, variance, coefficient of variation.
2. **`timing_features.py`**: Flow duration, inter-arrival time (IAT) statistics, packets/sec, bytes/sec.
3. **`tcp_features.py`**: SYN, ACK, FIN, RST, PSH, URG counts, SYN/ACK ratios.
4. **`protocol_features.py`**: Well-known application service identification (HTTP, HTTPS, DNS, SSH), encryption flags.
5. **`entropy_features.py`**: Shannon entropy $H(X) = -\sum p(x) \log_2 p(x)$ on packet sizes and traffic directions.
6. **`flow_analyzer.py`**: Behavioral traffic indicators (`is_long_flow`, `is_burst_traffic`, `is_large_transfer`, `is_high_pkt_rate`).
7. **`feature_validator.py`**: Sanitizes NaN / Inf values and validates numerical ranges.
8. **`feature_models.py`**: `FeatureVector` DTO supporting export formatters (`to_dict`, `to_json`, `to_numpy_list`).
