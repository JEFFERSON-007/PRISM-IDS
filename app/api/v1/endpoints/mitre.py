"""MITRE ATT&CK REST API Endpoints."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends
import structlog
from app.api.dependencies import get_current_user
from app.domain.mitre import MitreAttackCatalog
from app.models.user import User

router = APIRouter(prefix="/mitre", tags=["MITRE ATT&CK Framework"])
logger = structlog.get_logger("prism_ids.mitre_api")


@router.get("/matrix", response_model=List[Dict[str, Any]])
async def get_mitre_matrix(
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Fetch full MITRE ATT&CK techniques matrix (Requires JWT Auth)."""
    return MitreAttackCatalog.get_matrix()


@router.post("/map-alert", response_model=List[Dict[str, Any]])
async def map_alert_to_mitre(
    dst_port: int,
    protocol: str = "TCP",
    severity: str = "HIGH",
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Map alert parameters to corresponding MITRE ATT&CK techniques (Requires JWT Auth)."""
    return MitreAttackCatalog.map_alert_telemetry(dst_port=dst_port, protocol=protocol, severity=severity)
