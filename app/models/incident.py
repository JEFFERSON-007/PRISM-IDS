"""Incident SQLAlchemy ORM Model."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.database.base import Base


class Incident(Base):
    """Security Incident Management ORM Model."""

    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(String(64), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)

    severity = Column(String(20), nullable=False, default="MEDIUM", index=True)
    status = Column(String(20), nullable=False, default="OPEN", index=True)

    assigned_to_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    notes = Column(JSONB, nullable=True, default=list)
    correlation_id = Column(String(100), nullable=True, index=True)

    # Relationships
    assigned_user = relationship("User", backref="assigned_incidents", lazy="selectin")

    __table_args__ = (
        Index("ix_incidents_status_severity", "status", "severity"),
    )
