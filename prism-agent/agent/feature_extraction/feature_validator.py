"""Feature Vector Validation and Sanitization Engine."""

import math
from typing import Tuple
import structlog
from agent.feature_extraction.feature_models import FeatureVector

logger = structlog.get_logger("prism_agent.feature_validator")


class FeatureValidator:
    """Validates FeatureVector instances for NaNs, infinities, out-of-range bounds, and integrity."""

    @classmethod
    def validate_and_sanitize(cls, vector: FeatureVector, strict: bool = False) -> Tuple[bool, FeatureVector, str]:
        """Validate vector values, repair non-critical numerical flaws, or reject if invalid."""
        try:
            # Check required counts
            if vector.total_packets < 0 or vector.total_bytes < 0:
                return False, vector, "Negative packet or byte count"

            # Check NaNs and Infinities in numeric fields
            num_dict = vector.to_dict()
            for key, val in num_dict.items():
                if isinstance(val, float):
                    if math.isnan(val):
                        if strict:
                            return False, vector, f"NaN value found in field {key}"
                        # Repair NaN to 0.0
                        setattr(vector, key, 0.0)
                    elif math.isinf(val):
                        if strict:
                            return False, vector, f"Infinity value found in field {key}"
                        # Repair Inf to 0.0
                        setattr(vector, key, 0.0)

            return True, vector, "Valid"
        except Exception as exc:
            logger.error("Exception during FeatureVector validation", error=str(exc))
            return False, vector, f"Validation exception: {str(exc)}"
