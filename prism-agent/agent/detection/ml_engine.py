"""Machine Learning Inference Engine with Async Worker Thread Pool Offloading."""

import asyncio
from typing import Any, Optional
import structlog
from agent.core.config import agent_settings
from agent.detection.detection_models import MLPredictionResult
from agent.detection.model_loader import ModelLoader
from agent.feature_extraction.feature_models import FeatureVector

logger = structlog.get_logger("prism_agent.ml_engine")


class MLEngine:
    """Executes pre-trained machine learning model inference on FeatureVector DTOs."""

    def __init__(self, model: Optional[Any] = None) -> None:
        self.model = model or ModelLoader.load_model()
        self.threshold = agent_settings.ML_PREDICTION_THRESHOLD

    @property
    def is_available(self) -> bool:
        """Return True if model is loaded and ready for prediction."""
        return self.model is not None

    def predict(self, vector: FeatureVector) -> Optional[MLPredictionResult]:
        """Perform classification inference on FeatureVector synchronously."""
        if not self.is_available:
            return None

        try:
            features_array = [vector.to_numpy_list()]
            
            # Predict probabilities if supported
            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba(features_array)[0]
                # Class 1 probability (malicious)
                mal_prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
            else:
                pred = int(self.model.predict(features_array)[0])
                mal_prob = 1.0 if pred == 1 else 0.0

            is_malicious = mal_prob >= self.threshold
            confidence = round(mal_prob if is_malicious else (1.0 - mal_prob), 3)

            return MLPredictionResult(
                is_malicious=is_malicious,
                probability=round(mal_prob, 3),
                model_name=type(self.model).__name__,
                confidence=confidence,
            )
        except Exception as exc:
            logger.error("ML model inference failed", error=str(exc))
            return None

    async def predict_async(self, vector: FeatureVector) -> Optional[MLPredictionResult]:
        """Perform classification inference asynchronously by offloading CPU-bound matrix math to worker thread pool."""
        return await asyncio.to_thread(self.predict, vector)
