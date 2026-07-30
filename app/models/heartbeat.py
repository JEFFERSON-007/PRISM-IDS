"""Heartbeat ORM Model for recording agent health metrics."""

from datetime import datetime
import uuid
from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class Heartbeat(Base):
    """Historical heartbeat record submitted periodically by a monitoring agent."""

    __tablename__ = "heartbeats"

    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)

    # Resource Metrics
    cpu_usage: Mapped[float] = mapped_column(Float, nullable=False)
    ram_usage: Mapped[float] = mapped_column(Float, nullable=False)
    disk_usage: Mapped[float] = mapped_column(Float, nullable=False)
    network_status: Mapped[str] = mapped_column(String(50), default="ok", nullable=False)
    agent_version: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", back_populates="heartbeats")
