"""In-Memory Short-Term Conversation Memory for Analyst Q&A Sessions."""

from datetime import datetime, timezone
from typing import Dict, List, Optional


class ConversationMemory:
    """Manages short-term chat message history per session_id."""

    def __init__(self, max_history_per_session: int = 10) -> None:
        self.max_history = max_history_per_session
        self.sessions: Dict[str, List[Dict[str, str]]] = {}

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Retrieve conversation history list for a session."""
        return self.sessions.get(session_id, [])

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Append user or assistant message to session history."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        self.sessions[session_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Trim old messages to fit max_history limit
        if len(self.sessions[session_id]) > self.max_history:
            self.sessions[session_id] = self.sessions[session_id][-self.max_history:]

    def clear_session(self, session_id: str) -> None:
        """Reset conversation session."""
        if session_id in self.sessions:
            del self.sessions[session_id]


# Global memory manager
conversation_memory = ConversationMemory()
