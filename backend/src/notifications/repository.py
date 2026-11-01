import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.notifications.models import Notification


class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Notification:
        notif = Notification(**data, created_at=datetime.now(UTC))
        self.db.add(notif)
        await self.db.flush()
        return notif

    async def get_by_user(
        self,
        user_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        unread_only: bool = False,
    ) -> tuple[list[Notification], int, int]:
        base = select(Notification).where(Notification.user_id == user_id)

        unread_stmt = select(func.count()).select_from(
            select(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
            .subquery()
        )
        unread_count = (await self.db.execute(unread_stmt)).scalar() or 0

        if unread_only:
            base = base.where(Notification.is_read.is_(False))

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.db.execute(count_stmt)).scalar() or 0

        stmt = base.order_by(Notification.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), unread_count, total

    async def mark_read(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        stmt = (
            update(Notification)
            .where(Notification.id == notification_id, Notification.user_id == user_id)
            .values(is_read=True)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount > 0

    async def mark_all_read(self, user_id: uuid.UUID) -> int:
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
            .values(is_read=True)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount
