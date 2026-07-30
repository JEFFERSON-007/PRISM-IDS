"""AI Security Analyst (LLM Integration) REST API Endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from app.api.dependencies import get_current_user, get_db
from app.llm.chat_service import ChatService
from app.llm.llm_service import LLMService
from app.models.user import User
from app.schemas.llm import (
    AlertAnalysisRequest,
    ChatMessageRequest,
    ChatMessageResponse,
    LLMAnalysisResponse,
    LLMHealthResponse,
)

router = APIRouter(prefix="/llm", tags=["AI Security Analyst"])
logger = structlog.get_logger("prism_ids.llm_api")


@router.get("/health", response_model=LLMHealthResponse)
async def check_llm_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LLMHealthResponse:
    """Check Ollama API service status and model availability (Requires JWT Auth)."""
    service = LLMService(db)
    return await service.get_health()


@router.post("/analyze", response_model=LLMAnalysisResponse)
async def analyze_alert(
    request: AlertAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LLMAnalysisResponse:
    """Generate structured AI Security Briefing for an alert (Requires JWT Auth)."""
    service = LLMService(db)
    return await service.analyze_alert(alert_id=request.alert_id, alert_payload=request.alert_payload)


@router.post("/chat", response_model=ChatMessageResponse)
async def chat_with_analyst(
    request: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatMessageResponse:
    """Interactive SOC Analyst Q&A Session (Requires JWT Auth)."""
    chat_svc = ChatService()
    llm_svc = LLMService(db)

    alert_ctx = None
    if request.alert_id:
        brief = await llm_svc.analyze_alert(alert_id=request.alert_id)
        alert_ctx = brief.model_dump(mode="json")

    return await chat_svc.handle_chat_message(request, alert_context=alert_ctx)


@router.get("/summary", response_model=dict)
async def get_executive_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Generate high-level AI executive threat summary across recent critical alerts (Requires JWT Auth)."""
    service = LLMService(db)
    brief = await service.analyze_alert()
    return {
        "summary": brief.executive_summary,
        "critical_recommendations": [r.title for r in brief.remediation_actions],
        "model_used": brief.generated_by_model,
    }
