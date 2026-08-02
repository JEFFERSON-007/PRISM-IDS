"""Asynchronous HTTP Client for PRISM Server REST Interaction."""

import asyncio
from typing import Any, Dict, Optional
import httpx
import structlog
from agent.core.config import agent_settings
from agent.core.exceptions import AgentCommunicationError

logger = structlog.get_logger("prism_agent.http_client")


class AgentHTTPClient:
    """HTTP client wrapping httpx.AsyncClient with automatic agent header injection and retry logic."""

    def __init__(self, base_url: Optional[str] = None) -> None:
        self._custom_base_url = base_url
        self.agent_id: Optional[str] = None
        self.secret_key: Optional[str] = None

    @property
    def base_url(self) -> str:
        """Dynamic base URL evaluating active server settings."""
        return self._custom_base_url or agent_settings.SERVER_URL

    @base_url.setter
    def base_url(self, value: str) -> None:
        self._custom_base_url = value

    def set_credentials(self, agent_id: str, secret_key: str) -> None:
        """Configure agent authentication credentials."""
        self.agent_id = agent_id
        self.secret_key = secret_key

    def _get_headers(self) -> Dict[str, str]:
        """Construct request headers including agent authentication credentials."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"PRISM-IDS-Agent/{agent_settings.AGENT_VERSION}",
        }
        if self.agent_id and self.secret_key:
            headers["X-Agent-ID"] = self.agent_id
            headers["X-Agent-Secret"] = self.secret_key
        return headers

    async def request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retries: int = 3,
    ) -> Dict[str, Any]:
        """Execute HTTP request with automatic retry and exponential backoff."""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = self._get_headers()

        backoff = 1.0
        for attempt in range(1, retries + 1):
            try:
                async with httpx.AsyncClient(timeout=agent_settings.HTTP_TIMEOUT) as client:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        json=json_data,
                        params=params,
                    )

                if response.is_success:
                    return response.json()

                logger.warning(
                    "HTTP Request non-2xx response",
                    method=method,
                    url=url,
                    status_code=response.status_code,
                    attempt=attempt,
                )

                if response.status_code in (401, 403):
                    raise AgentCommunicationError(
                        f"Authentication rejected by server ({response.status_code}): {response.text}"
                    )

            except httpx.RequestError as exc:
                logger.warning(
                    "HTTP Connection error",
                    method=method,
                    url=url,
                    error=str(exc),
                    attempt=attempt,
                )

            if attempt < retries:
                await asyncio.sleep(backoff)
                backoff *= 2.0

        raise AgentCommunicationError(f"HTTP {method} {url} failed after {retries} attempts.")

    async def post(self, endpoint: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convenience method for HTTP POST."""
        return await self.request("POST", endpoint, json_data=json_data)

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Convenience method for HTTP GET."""
        return await self.request("GET", endpoint, params=params)
