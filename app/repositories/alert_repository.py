"""Alert Database Repository."""

import math

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import uuid
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.alert import Alert
from app.repositories.base import BaseRepository


class AlertRepository(BaseRepository[Alert]):
    """Repository handling database queries for security alerts."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Alert, session)

    async def get_by_alert_id(self, alert_id: str) -> Optional[Alert]:
        """Fetch alert by unique alert_id string."""
        stmt = select(Alert).where(Alert.alert_id == alert_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def filter_alerts(
        self,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        protocol: Optional[str] = None,
        detection_method: Optional[str] = None,
        src_ip: Optional[str] = None,
        dst_ip: Optional[str] = None,
        agent_id: Optional[uuid.UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        search_query: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Alert], int, int]:
        """Query alerts with dynamic filtering, full-text search, and pagination."""
        stmt = select(Alert)
        count_stmt = select(func.count(Alert.id))

        filters = []
        if severity:
            filters.append(Alert.severity == severity.upper())
        if status:
            filters.append(Alert.status == status.upper())
        if protocol:
            filters.append(Alert.protocol == protocol.upper())
        if detection_method:
            filters.append(Alert.detection_method == detection_method.upper())
        if src_ip:
            filters.append(Alert.src_ip == src_ip)
        if dst_ip:
            filters.append(Alert.dst_ip == dst_ip)
        if agent_id:
            filters.append(Alert.agent_id == agent_id)
        if start_time:
            filters.append(Alert.timestamp >= start_time)
        if end_time:
            filters.append(Alert.timestamp <= end_time)

        if search_query:
            pattern = f"%{search_query}%"
            filters.append(
                (Alert.src_ip.ilike(pattern))
                | (Alert.dst_ip.ilike(pattern))
                | (Alert.alert_id.ilike(pattern))
                | (Alert.protocol.ilike(pattern))
                | (Alert.correlation_id.ilike(pattern))
            )

        if filters:
            stmt = stmt.where(*filters)
            count_stmt = count_stmt.where(*filters)

        # Count total matching records
        total_res = await self.session.execute(count_stmt)
        total_records = total_res.scalar() or 0

        # Pagination & Sorting (newest first)
        stmt = stmt.order_by(Alert.timestamp.desc())
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        total_pages = math.ceil(total_records / page_size) if page_size > 0 else 1

        return items, total_records, total_pages

    async def get_severity_counts(self) -> Dict[str, int]:
        """Aggregate total count of alerts grouped by severity."""
        stmt = select(Alert.severity, func.count(Alert.id)).group_by(Alert.severity)
        res = await self.session.execute(stmt)
        counts = {row[0].upper(): row[1] for row in res.all()}
        return counts

    async def get_average_risk_score(self) -> float:
        """Compute average risk score across all stored alerts."""
        stmt = select(func.avg(Alert.risk_score))
        res = await self.session.execute(stmt)
        avg = res.scalar()
        return round(float(avg), 1) if avg else 0.0

    async def get_top_target_hosts(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetch top targeted destination IPs by alert count."""
        stmt = (
            select(Alert.dst_ip, func.count(Alert.id).label("count"), func.max(Alert.severity).label("max_sev"))
            .group_by(Alert.dst_ip)
            .order_by(func.count(Alert.id).desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return [{"dst_ip": r[0], "alert_count": r[1], "highest_severity": r[2]} for r in res.all()]

    async def get_top_attacker_ips(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetch top attacking source IPs by alert count."""
        stmt = (
            select(Alert.src_ip, func.count(Alert.id).label("count"), func.max(Alert.severity).label("max_sev"))
            .group_by(Alert.src_ip)
            .order_by(func.count(Alert.id).desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return [{"src_ip": r[0], "alert_count": r[1], "highest_severity": r[2]} for r in res.all()]

    async def get_protocol_distribution(self) -> List[Dict[str, Any]]:
        """Calculate protocol traffic distribution."""
        stmt = select(Alert.protocol, func.count(Alert.id)).group_by(Alert.protocol)
        res = await self.session.execute(stmt)
        rows = res.all()
        total = sum(r[1] for r in rows) or 1
        return [
            {"protocol": r[0], "count": r[1], "percentage": round((r[1] / total) * 100.0, 1)}
            for r in rows
        ]
