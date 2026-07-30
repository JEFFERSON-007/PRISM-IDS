"""Secure Local Credentials Persistence Store."""

import json
import os
from typing import Dict, Optional
import structlog
from agent.core.config import agent_settings

logger = structlog.get_logger("prism_agent.credentials")


class CredentialsStore:
    """Manages local storage and retrieval of assigned agent credentials."""

    def __init__(self, filepath: Optional[str] = None) -> None:
        self.filepath = filepath or agent_settings.CREDENTIALS_FILE

    def save_credentials(self, agent_id: str, secret_key: str) -> None:
        """Save issued agent credentials to local disk with strict permissions."""
        data = {
            "agent_id": agent_id,
            "secret_key": secret_key,
            "agent_name": agent_settings.AGENT_NAME,
        }
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            # Restrict permissions on Linux/macOS to user-only read/write (0600)
            if hasattr(os, "chmod"):
                try:
                    os.chmod(self.filepath, 0o600)
                except Exception:
                    pass

            logger.info("Saved agent credentials locally", filepath=self.filepath, agent_id=agent_id)
        except Exception as exc:
            logger.error("Failed to save local credentials", error=str(exc))
            raise

    def load_credentials(self) -> Optional[Dict[str, str]]:
        """Load stored credentials from file if present."""
        if not os.path.exists(self.filepath):
            return None

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "agent_id" in data and "secret_key" in data:
                    return data
        except Exception as exc:
            logger.warning("Could not parse local credentials file", error=str(exc))

        return None

    def clear(self) -> None:
        """Delete local stored credentials."""
        if os.path.exists(self.filepath):
            try:
                os.remove(self.filepath)
                logger.info("Cleared local credentials file")
            except Exception as exc:
                logger.error("Failed to remove credentials file", error=str(exc))
