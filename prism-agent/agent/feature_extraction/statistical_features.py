"""Statistical Feature Calculation Helpers."""

import math
from typing import List, Tuple


class StatisticalFeatures:
    """Calculates statistical summary metrics for data sequences."""

    @staticmethod
    def compute_stats(values: List[float]) -> Tuple[float, float, float, float, float]:
        """Compute (min, max, mean, std_dev, variance). Safe against empty input."""
        if not values:
            return 0.0, 0.0, 0.0, 0.0, 0.0

        n = len(values)
        min_v = float(min(values))
        max_v = float(max(values))
        mean_v = float(sum(values) / n)

        if n <= 1:
            return min_v, max_v, mean_v, 0.0, 0.0

        variance_v = sum((x - mean_v) ** 2 for x in values) / (n - 1)
        std_v = math.sqrt(variance_v)

        return min_v, max_v, round(mean_v, 3), round(std_v, 3), round(variance_v, 3)

    @staticmethod
    def coefficient_of_variation(mean_val: float, std_val: float) -> float:
        """Compute coefficient of variation (std / mean)."""
        if mean_val <= 0:
            return 0.0
        return round(std_val / mean_val, 3)
