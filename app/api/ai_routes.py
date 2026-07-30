"""AI Security Analyst REST and Streaming API Endpoints (/api/ai/*)."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from app.api.dependencies import get_current_user
from app.database.session import get_db
from app.llm.llm_service import LLMService
from app.models.user import User
from app.schemas.ai import (
    AIAlertSummaryResponse,
    AIChatRequest,
    AIChatResponse,
    AIHealthResponse,
    AIReportRequest,
    AIReportResponse,
)

logger = structlog.get_logger("prism_ids.ai_routes")

router = APIRouter(prefix="/api/ai", tags=["AI Security Analyst"])


@router.get("/health", response_model=AIHealthResponse, summary="Check Ollama AI Analyst Health")
async def get_ai_health() -> AIHealthResponse:
    """Check Ollama service status, model availability (qwen2.5:3b), and load state."""
    service = LLMService()
    return await service.get_health()


@router.post("/alert/{id}/summary", response_model=AIAlertSummaryResponse, summary="Generate or fetch cached AI alert summary")
async def get_alert_summary(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AIAlertSummaryResponse:
    """Load alert from database, build context, send to Ollama (or return cached summary), and return structured JSON."""
    service = LLMService(session=db)
    try:
        return await service.get_alert_summary(alert_id=id)
    except Exception as exc:
        logger.error("Failed to generate AI summary for alert", alert_id=id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI summary: {str(exc)}",
        )


@router.post("/chat", summary="Interactive AI SOC Analyst Chat Q&A")
async def ai_chat(
    payload: AIChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ask security questions to AI Analyst. Supports JSON or SSE streaming response."""
    service = LLMService(session=db)

    if payload.stream:
        async def event_generator():
            async for chunk in service.stream_chat(prompt=payload.prompt, alert_id=payload.alert_id):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    return await service.chat(prompt=payload.prompt, alert_id=payload.alert_id)


@router.post("/report", response_model=AIReportResponse, summary="Generate AI Executive Security Report")
async def generate_report(
    payload: Optional[AIReportRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AIReportResponse:
    """Generate comprehensive executive report covering top attacks, targeted assets, MITRE techniques, and risk trends."""
    service = LLMService(session=db)
    timeframe = payload.timeframe if payload else "24h"
    top_limit = payload.top_limit if payload else 5
    return await service.generate_executive_report(timeframe=timeframe, top_limit=top_limit)
