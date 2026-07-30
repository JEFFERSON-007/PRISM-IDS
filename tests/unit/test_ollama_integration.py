"""Unit tests for Ollama Qwen2.5:3B AI Analyst Integration."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from app.llm.cache import LLMCache, llm_cache
from app.llm.context_builder import ContextBuilder
from app.llm.ollama_client import OllamaClient
from app.llm.prompt_builder import PromptBuilder
from app.llm.llm_service import LLMService
from app.schemas.ai import AIAlertSummaryResponse, AIChatResponse, AIHealthResponse, AIReportResponse


def test_prompt_builder_system_prompt() -> None:
    """Verify system prompt enforces SOC L3 non-detection directive."""
    expected = (
        "You are a Senior SOC Level-3 Cybersecurity Analyst. "
        "The attack has already been detected. "
        "Never decide whether traffic is malicious. "
        "Your role is only to explain and recommend."
    )
    assert PromptBuilder.SYSTEM_SECURITY_ANALYST_PROMPT == expected


def test_prompt_builder_alert_prompt() -> None:
    """Verify alert analysis prompt includes telemetry context."""
    context = {"alert_id": "ALT-1234", "severity": "HIGH", "risk_score": 90.0}
    prompt = PromptBuilder.build_alert_analysis_prompt(context)
    assert "ALT-1234" in prompt
    assert "remediation_actions" in prompt
    assert "mitre_attack_mapping" in prompt


def test_llm_cache_operations() -> None:
    """Verify in-memory LLMCache set, get, and clear."""
    cache = LLMCache(ttl_seconds=300)
    cache.set("ALT-9999", {"executive_summary": "Test summary"})

    result = cache.get("ALT-9999")
    assert result is not None
    assert result["executive_summary"] == "Test summary"

    cache.clear()
    assert cache.get("ALT-9999") is None


@pytest.mark.asyncio
async def test_ollama_client_check_health() -> None:
    """Test OllamaClient health check parsing."""
    client = OllamaClient()
    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_res.json.return_value = {"models": [{"name": "qwen2.5:3b"}, {"name": "llama3.2:latest"}]}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_res):
        health = await client.check_health()
        assert health["online"] is True
        assert health["model_available"] is True
        assert "qwen2.5:3b" in health["available_models"]


@pytest.mark.asyncio
async def test_llm_service_get_health() -> None:
    """Test LLMService health check wrapper."""
    mock_client = MagicMock()
    mock_client.model = "qwen2.5:3b"
    mock_client.check_health = AsyncMock(return_value={
        "online": True,
        "model_name": "qwen2.5:3b",
        "model_available": True,
        "loaded": True,
        "available_models": ["qwen2.5:3b"],
    })

    service = LLMService(ollama_client=mock_client)
    res = await service.get_health()
    assert isinstance(res, AIHealthResponse)
    assert res.online is True
    assert res.model_name == "qwen2.5:3b"


@pytest.mark.asyncio
async def test_llm_service_chat() -> None:
    """Test LLMService chat generation."""
    mock_client = MagicMock()
    mock_client.model = "qwen2.5:3b"
    mock_client.generate = AsyncMock(return_value="Port scanning T1046 is used to map open services.")

    service = LLMService(ollama_client=mock_client)
    res = await service.chat(prompt="Explain port scanning")
    assert isinstance(res, AIChatResponse)
    assert "Port scanning" in res.response
    assert res.latency_ms >= 0


@pytest.mark.asyncio
async def test_llm_service_executive_report() -> None:
    """Test LLMService executive report generation."""
    service = LLMService()
    report = await service.generate_executive_report()
    assert isinstance(report, AIReportResponse)
    assert len(report.recommendations) > 0
    assert len(report.common_mitre_techniques) > 0
