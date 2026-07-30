"""Unit tests for AI Security Analyst LLM Integration."""

import pytest
from app.llm.context_builder import ContextBuilder
from app.llm.prompt_builder import PromptBuilder
from app.llm.recommendation_engine import RecommendationEngine
from app.llm.response_parser import ResponseParser


def test_context_builder() -> None:
    """Test sanitizing alert payload into prompt context."""
    raw_alert = {
        "alert_id": "ALT-100",
        "severity": "CRITICAL",
        "risk_score": 95.0,
        "src_ip": "192.168.1.50",
        "dst_ip": "10.0.0.1",
        "dst_port": 80,
        "protocol": "TCP",
    }

    ctx = ContextBuilder.build_alert_context(raw_alert)
    assert ctx["alert_id"] == "ALT-100"
    assert ctx["severity"] == "CRITICAL"
    assert ctx["network_flow"]["source_ip"] == "192.168.1.50"


def test_prompt_builder() -> None:
    """Test rendering alert analysis prompt."""
    ctx = {"alert_id": "ALT-100", "severity": "HIGH"}
    prompt = PromptBuilder.build_alert_analysis_prompt(ctx)
    assert "ALT-100" in prompt
    assert "executive_summary" in prompt


def test_recommendation_engine() -> None:
    """Test rule-based fallback recommendation engine."""
    ctx = {
        "severity": "CRITICAL",
        "network_flow": {"source_ip": "192.168.1.50", "destination_ip": "10.0.0.1", "destination_port": 80},
    }

    mitre_list, remediations = RecommendationEngine.generate_recommendations(ctx)
    assert len(mitre_list) > 0
    assert remediations[0].priority == 1
    assert remediations[0].action_type == "BLOCK_IP"
    assert "192.168.1.50" in remediations[0].title
