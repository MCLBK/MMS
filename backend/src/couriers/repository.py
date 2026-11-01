import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.delivery.models import CourierProfile, CourierStatus


class CourierRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self, courier_id: uuid.UUID, company_id: uuid.UUID
    ) -> CourierProfile | None:
        result = await self.db.execute(
            select(CourierProfile)
            .options(selectinload(CourierProfile.user))
            .where(CourierProfile.id == courier_id, CourierProfile.company_id == company_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self, user_id: uuid.UUID, company_id: uuid.UUID
    ) -> CourierProfile | None:
        result = await self.db.execute(
            select(CourierProfile).where(
                CourierProfile.user_id == user_id,
                CourierProfile.company_id == company_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_couriers(
        self,
        company_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        status_filter: CourierStatus | None = None,
        active_only: bool = False,
    ) -> tuple[list[CourierProfile], int]:
        base = select(CourierProfile).where(CourierProfile.company_id == company_id)
        if status_filter:
            base = base.where(CourierProfile.status == status_filter)
        if active_only:
            base = base.where(CourierProfile.is_active.is_(True))

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.db.execute(count_stmt)).scalar() or 0

        stmt = (
            base.options(selectinload(CourierProfile.user))
            .order_by(CourierProfile.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def create(self, data: dict) -> CourierProfile:
        profile = CourierProfile(**data)
        self.db.add(profile)
        await self.db.flush()
        return profile

    async def update(self, profile: CourierProfile, data: dict) -> CourierProfile:
        for key, value in data.items():
            if value is not None:
                setattr(profile, key, value)
        await self.db.flush()
        return profile

    async def update_position(
        self, profile: CourierProfile, lat: float, lng: float
    ) -> CourierProfile:
        profile.current_lat = lat
        profile.current_lng = lng
        profile.last_position_at = datetime.now(timezone.utc)
        await self.db.flush()
        return profile

    async def get_available_couriers(
        self, company_id: uuid.UUID
    ) -> list[CourierProfile]:
        stmt = (
            select(CourierProfile)
            .options(selectinload(CourierProfile.user))
            .where(
                CourierProfile.company_id == company_id,
                CourierProfile.is_active.is_(True),
                CourierProfile.status == CourierStatus.AVAILABLE,
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
