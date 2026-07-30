# Machine Learning Inference Subsystem

The Machine Learning Engine deserializes pre-trained Scikit-learn models (`.joblib` or `.pkl`) specified by `MODEL_PATH`.

## Graceful Standby Mode

If no pre-trained model file exists at `MODEL_PATH`, the ML Engine enters **standby mode** automatically without raising unhandled runtime exceptions. The Signature Engine continues operating independently.
