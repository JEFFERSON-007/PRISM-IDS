"""Alert SQLAlchemy ORM Model."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.database.base import Base


class Alert(Base):
    """Stored Security Alert ORM Model."""

    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(String(64), unique=True, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    first_seen = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    detection_id = Column(String(64), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    flow_id = Column(String(64), nullable=False)

    src_ip = Column(String(45), nullable=False, index=True)
    dst_ip = Column(String(45), nullable=False, index=True)
    src_port = Column(Integer, nullable=False)
    dst_port = Column(Integer, nullable=False)
    protocol = Column(String(16), nullable=False, index=True)

    risk_score = Column(Float, nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    detection_method = Column(String(30), nullable=False)

    matched_rules = Column(JSONB, nullable=True)
    ml_prediction = Column(JSONB, nullable=True)
    confidence = Column(Float, nullable=False)

    evidence_summary = Column(JSONB, nullable=True)
    status = Column(String(20), nullable=False, default="OPEN", index=True)
    occurrence_count = Column(Integer, nullable=False, default=1)
    correlation_id = Column(String(100), nullable=True, index=True)

    # Relationships
    agent = relationship("Agent", backref="alerts", lazy="selectin")

    __table_args__ = (
        Index("ix_alerts_severity_timestamp", "severity", "timestamp"),
        Index("ix_alerts_src_ip_timestamp", "src_ip", "timestamp"),
        Index("ix_alerts_dst_ip_timestamp", "dst_ip", "timestamp"),
    )
