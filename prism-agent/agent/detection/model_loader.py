"""Safe Pre-Trained Machine Learning Model Loader."""

import os
from typing import Any, Optional
import joblib
import structlog
from agent.core.config import agent_settings

logger = structlog.get_logger("prism_agent.model_loader")


class ModelLoader:
    """Safely loads Scikit-learn / Joblib model file with fallback handling."""

    @classmethod
    def load_model(cls, model_path: Optional[str] = None) -> Optional[Any]:
        """Load joblib model file from disk. Return None if missing or corrupt."""
        target_path = model_path or agent_settings.MODEL_PATH

        if not os.path.exists(target_path):
            logger.info("No pre-trained ML model file found at path; ML Engine running in standby", path=target_path)
            return None

        try:
            model = joblib.load(target_path)
            logger.info("Successfully loaded pre-trained ML model", path=target_path, model_type=type(model).__name__)
            return model
        except Exception as exc:
            logger.error("Failed to deserialize ML model file", path=target_path, error=str(exc))
            return None
