"""In-memory cache for LLM analysis responses."""

from datetime import datetime, timezone
import hashlib
from typing import Any, Dict, Optional


class LLMCache:
    """Simple thread-safe in-memory cache for AI Security Analyst responses."""

    def __init__(self, ttl_seconds: int = 3600) -> None:
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds

    def _hash_key(self, key: str) -> str:
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def get(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached analysis if not expired."""
        key = self._hash_key(alert_id)
        entry = self._cache.get(key)
        if not entry:
            return None

        created_at = entry.get("_cached_at", 0)
        now = datetime.now(timezone.utc).timestamp()
        if (now - created_at) > self.ttl_seconds:
            del self._cache[key]
            return None

        result = dict(entry)
        result.pop("_cached_at", None)
        return result

    def set(self, alert_id: str, data: Dict[str, Any]) -> None:
        """Store analysis response in cache."""
        key = self._hash_key(alert_id)
        entry = dict(data)
        entry["_cached_at"] = datetime.now(timezone.utc).timestamp()
        self._cache[key] = entry

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()


# Global cache instance
llm_cache = LLMCache()
