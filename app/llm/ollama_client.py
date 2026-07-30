"""Async HTTP Client for Ollama LLM Runtime."""

import json
from typing import Any, AsyncGenerator, Dict, List, Optional
import httpx
import structlog
from app.core.config import settings

logger = structlog.get_logger("prism_ids.ollama_client")


class OllamaClient:
    """Async HTTP Client communicating with local Ollama API service."""

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None) -> None:
        self.base_url = (base_url or getattr(settings, "OLLAMA_URL", None) or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or getattr(settings, "OLLAMA_MODEL", "qwen2.5:3b")
        self.timeout = float(getattr(settings, "OLLAMA_TIMEOUT", 30))

    async def check_health(self) -> Dict[str, Any]:
        """Check Ollama API service health and verify model availability."""
        tags_url = f"{self.base_url}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(tags_url)
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    # Check if requested model or any matching base model (e.g. qwen2.5:3b or qwen:3b) is present
                    target_base = self.model.split(":")[0]
                    model_available = any(self.model in m or target_base in m for m in models)
                    return {
                        "online": True,
                        "model_name": self.model,
                        "model_available": model_available,
                        "loaded": model_available,
                        "available_models": models,
                    }
        except Exception as exc:
            logger.warning("Ollama API health check failed", url=tags_url, error=str(exc))

        return {
            "online": False,
            "model_name": self.model,
            "model_available": False,
            "loaded": False,
            "available_models": [],
        }

    async def generate(
        self, prompt: str, system_prompt: Optional[str] = None, json_format: bool = True, retries: int = 2
    ) -> Optional[str]:
        """Send prompt to Ollama /api/generate endpoint with retry and timeout support."""
        url = f"{self.base_url}/api/generate"
        payload: Dict[str, Any] = {
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

        for attempt in range(1, retries + 2):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    logger.info("Executing Ollama LLM inference", model=self.model, attempt=attempt, prompt_len=len(prompt))
                    res = await client.post(url, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        response_text = data.get("response", "")
                        logger.info("Ollama LLM inference succeeded", response_len=len(response_text))
                        return response_text
                    else:
                        logger.error("Ollama API error response", status_code=res.status_code, body=res.text)
            except httpx.TimeoutException:
                logger.error("Ollama LLM request timed out", timeout=self.timeout, attempt=attempt)
            except Exception as exc:
                logger.error("Failed to execute Ollama LLM inference", error=str(exc), attempt=attempt)

        return None

    async def generate_stream(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Stream response chunks from Ollama /api/generate endpoint."""
        url = f"{self.base_url}/api/generate"
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
            },
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code == 200:
                        async for line in response.aiter_lines():
                            if line and line.strip():
                                try:
                                    chunk = json.loads(line)
                                    text_token = chunk.get("response", "")
                                    if text_token:
                                        yield text_token
                                except Exception:
                                    yield line
        except Exception as exc:
            logger.error("Error streaming from Ollama API", error=str(exc))
            yield f"\n[Error streaming AI response: {str(exc)}]\n"
