"""Unit tests for ModelLoader fallback behavior."""

from agent.detection.model_loader import ModelLoader


def test_model_loader_nonexistent_file() -> None:
    """Test ModelLoader returns None when model file is missing."""
    model = ModelLoader.load_model("nonexistent_path.joblib")
    assert model is None
