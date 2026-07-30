"""Async HTTP Client for Ollama LLM Runtime."""

from typing import Any, Dict, List, Optional
import httpx
import structlog
from app.core.config import settings

logger = structlog.get_logger("prism_ids.ollama_client")


class OllamaClient:
    """Async HTTP Client communicating with local Ollama API service."""

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None) -> None:
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT_SECONDS

    async def check_health(self) -> Dict[str, Any]:
        """Check Ollama API service health and fetch list of loaded models."""
        url = f"{self.base_url}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    model_available = any(self.model in m for m in models)
                    return {
                        "online": True,
                        "available_models": models,
                        "configured_model_available": model_available,
                    }
        except Exception as exc:
            logger.warning("Ollama API health check failed", url=url, error=str(exc))

        return {
            "online": False,
            "available_models": [],
            "configured_model_available": False,
        }

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, json_format: bool = True) -> Optional[str]:
        """Send prompt to Ollama /api/generate endpoint."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
            },
        }

        if system_prompt:
            payload["system"] = system_prompt
        if json_format:
            payload["format"] = "json"

        try:
            async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                logger.info("Executing Ollama LLM inference", model=self.model, prompt_len=len(prompt))
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    response_text = data.get("response", "")
                    logger.info("Ollama LLM inference succeeded", response_len=len(response_text))
                    return response_text
                else:
                    logger.error("Ollama API error response", status_code=res.status_code, body=res.text)
        except httpx.TimeoutException:
            logger.error("Ollama LLM request timed out", timeout=self.timeout)
        except Exception as exc:
            logger.error("Failed to execute Ollama LLM inference", error=str(exc))

        return None
