import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.audit import AuditLog


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        action: str,
        resource_type: str,
        resource_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        company_id: uuid.UUID | None = None,
        details: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            user_id=user_id,
            company_id=company_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.now(UTC),
        )
        self.db.add(entry)
        await self.db.flush()
        return entry

    async def list_logs(
        self,
        company_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 50,
        action_filter: str | None = None,
        resource_type_filter: str | None = None,
    ) -> tuple[list[AuditLog], int]:
        base = select(AuditLog)

        if company_id:
            base = base.where(AuditLog.company_id == company_id)
        if action_filter:
            base = base.where(AuditLog.action == action_filter)
        if resource_type_filter:
            base = base.where(AuditLog.resource_type == resource_type_filter)

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.db.execute(count_stmt)).scalar() or 0

        stmt = base.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total
