"""Agent ORM Model representing deployed monitoring agents."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class Agent(Base):
    """Registered PRISM monitoring agent entity."""

    __tablename__ = "agents"

    agent_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hostname: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    operating_system: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)

    # Security Credentials
    secret_key_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Status & Heartbeat Tracking
    registration_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_heartbeat: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    health_status: Mapped[str] = mapped_column(String(20), default="unknown", nullable=False)

    # Relationships
    heartbeats: Mapped[List["Heartbeat"]] = relationship(
        "Heartbeat", back_populates="agent", cascade="all, delete-orphan"
    )
    configuration: Mapped[Optional["AgentConfiguration"]] = relationship(
        "AgentConfiguration", back_populates="agent", uselist=False, cascade="all, delete-orphan"
    )
