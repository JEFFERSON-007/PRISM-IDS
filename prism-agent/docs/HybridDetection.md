# Hybrid Intrusion Detection Engine Architecture

The **Hybrid Intrusion Detection Engine** combines deterministic signature-based rule evaluation with machine learning classification inference to detect malicious network activity.

```
┌────────────────────────────────────────────────────────────┐
│               Feature Extraction Output Queue              │
│                (Pushes FeatureVector DTOs)                 │
└─────────────────────────────┬──────────────────────────────┘
                              │
               ┌──────────────┴──────────────┐
               │                             │
┌──────────────▼─────────────┐ ┌─────────────▼──────────────┐
│      Signature Engine      │ │     Machine Learning       │
│  (Evaluates BPF / Rules)   │ │  (Joblib Model Inference)  │
└──────────────┬─────────────┘ └─────────────┬──────────────┘
               │                             │
               └──────────────┬──────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                    Confidence Engine                       │
│    (Calculates weighted confidence score C in [0.0, 1.0])  │
└─────────────────────────────┬──────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                    Detection Fusion                        │
│    (Unifies findings into standardized DetectionResult)    │
└─────────────────────────────┬──────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                  Bounded Detection Queue                   │
│      (Buffers DetectionResults for Risk Engine)            │
└────────────────────────────────────────────────────────────┘
```

---

## Subsystem Modules

1. **`signature_engine.py`**: Evaluates `FeatureVector` DTOs against JSON signature rules (`SIG-001` Port Scan, `SIG-002` SYN Flood, `SIG-003` ICMP Flood, etc.).
2. **`ml_engine.py`**: Executes Scikit-learn model inference (`RandomForestClassifier`, `XGBoost`, `LightGBM`, etc.) using `FeatureVector.to_numpy_list()`.
3. **`confidence_engine.py`**: Computes weighted confidence scores based on rule match severity and ML probability.
4. **`detection_fusion.py`**: Unifies signature matches and ML predictions into a single `DetectionResult` payload.
5. **`detection_queue.py`**: Bounded output queue buffering detections for the downstream Risk Engine.
