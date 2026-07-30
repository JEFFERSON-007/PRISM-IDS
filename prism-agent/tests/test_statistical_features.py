"""Unit tests for StatisticalFeatures calculator."""

from agent.feature_extraction.statistical_features import StatisticalFeatures


def test_statistical_features_computation() -> None:
    """Test min, max, mean, std dev, variance on list of floats."""
    data = [10.0, 20.0, 30.0, 40.0, 50.0]
    min_v, max_v, mean_v, std_v, var_v = StatisticalFeatures.compute_stats(data)

    assert min_v == 10.0
    assert max_v == 50.0
    assert mean_v == 30.0
    assert round(std_v, 2) == 15.81
    assert round(var_v, 1) == 250.0


def test_empty_statistical_features() -> None:
    """Test safe fallback on empty list."""
    min_v, max_v, mean_v, std_v, var_v = StatisticalFeatures.compute_stats([])
    assert (min_v, max_v, mean_v, std_v, var_v) == (0.0, 0.0, 0.0, 0.0, 0.0)
