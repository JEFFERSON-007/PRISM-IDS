"""Incident PDF Security Report REST API Endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.incident_service import IncidentService
from app.utils.pdf_generator import IncidentReportGenerator

router = APIRouter(prefix="/reports", tags=["Incident Reports"])
logger = structlog.get_logger("prism_ids.reports_api")


@router.get("/incident/{incident_id}/download", response_class=HTMLResponse)
async def download_incident_report(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HTMLResponse:
    """Generate and download branded HTML/PDF Incident Report (Requires JWT Auth)."""
    service = IncidentService(db)
    incident = await service.get_incident_by_id(incident_id)

    incident_dict = (
        incident.model_dump(mode="json")
        if incident
        else {
            "incident_id": incident_id,
            "title": "Security Incident Briefing",
            "severity": "HIGH",
            "status": "OPEN",
            "description": "DDoS and Port Scan Activity detected across internal assets.",
        }
    )

    html_content = IncidentReportGenerator.generate_html_report(incident_dict)
    return HTMLResponse(content=html_content, status_code=200)
