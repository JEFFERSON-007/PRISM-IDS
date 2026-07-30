"""Analyst Q&A Chat Service."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
import structlog
from app.llm.conversation_memory import conversation_memory
from app.llm.ollama_client import OllamaClient
from app.llm.prompt_builder import PromptBuilder
from app.schemas.llm import ChatMessageRequest, ChatMessageResponse

logger = structlog.get_logger("prism_ids.chat_service")


class ChatService:
    """Service handling interactive SOC Analyst chat queries."""

    def __init__(self, ollama_client: Optional[OllamaClient] = None) -> None:
        self.client = ollama_client or OllamaClient()

    async def handle_chat_message(self, request: ChatMessageRequest, alert_context: Optional[Dict[str, Any]] = None) -> ChatMessageResponse:
        """Process analyst chat query and generate intelligent AI response."""
        history = conversation_memory.get_history(request.session_id)
        prompt = PromptBuilder.build_chat_prompt(alert_context, request.message, history)

        # 1. Record user query in memory
        conversation_memory.add_message(request.session_id, "user", request.message)

        # 2. Execute LLM inference via Ollama
        reply_text = await self.client.generate(
            prompt, system_prompt=PromptBuilder.SYSTEM_SECURITY_ANALYST_PROMPT, json_format=False
        )

        model_used = self.client.model
        if not reply_text:
            model_used = "Rule-Based Fallback Engine"
            reply_text = (
                f"I am assisting with alert context. Query recorded: '{request.message}'. "
                "Recommendation: Inspect flow ports, verify IP reputation on VirusTotal, and review signature rules."
            )

        # 3. Record assistant reply in memory
        conversation_memory.add_message(request.session_id, "assistant", reply_text)

        return ChatMessageResponse(
            session_id=request.session_id,
            reply=reply_text,
            timestamp=datetime.now(timezone.utc),
            model_used=model_used,
        )
