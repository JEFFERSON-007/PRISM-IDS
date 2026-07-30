"""Agent Configuration ORM Model."""

from typing import Any, Dict, Optional
import uuid
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class AgentConfiguration(Base):
    """Dynamic configuration template assigned to a specific monitoring agent."""

    __tablename__ = "agent_configurations"

    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Agent operational settings
    capture_interface: Mapped[str] = mapped_column(String(50), default="eth0", nullable=False)
    packet_filters: Mapped[str] = mapped_column(String(255), default="ip", nullable=False)
    log_level: Mapped[str] = mapped_column(String(20), default="INFO", nullable=False)
    sampling_rate: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    custom_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", back_populates="configuration")
