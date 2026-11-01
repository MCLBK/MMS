import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.delivery.models import CourierProfile
from src.tracking.models import GPSLocation


class TrackingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_position(self, courier_id: uuid.UUID, data: dict) -> GPSLocation:
        location = GPSLocation(
            courier_id=courier_id,
            recorded_at=datetime.now(UTC),
            **data,
        )
        self.db.add(location)
        await self.db.flush()
        return location

    async def get_courier_history(
        self,
        courier_id: uuid.UUID,
        minutes: int = 60,
        limit: int = 500,
    ) -> list[GPSLocation]:
        since = datetime.now(UTC) - timedelta(minutes=minutes)
        stmt = (
            select(GPSLocation)
            .where(
                GPSLocation.courier_id == courier_id,
                GPSLocation.recorded_at >= since,
            )
            .order_by(GPSLocation.recorded_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_assignment_track(self, assignment_id: uuid.UUID) -> list[GPSLocation]:
        stmt = (
            select(GPSLocation)
            .where(GPSLocation.assignment_id == assignment_id)
            .order_by(GPSLocation.recorded_at.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_live_positions(self, company_id: uuid.UUID) -> list[CourierProfile]:
        stmt = (
            select(CourierProfile)
            .options(selectinload(CourierProfile.user))
            .where(
                CourierProfile.company_id == company_id,
                CourierProfile.is_active.is_(True),
                CourierProfile.current_lat.isnot(None),
                CourierProfile.current_lng.isnot(None),
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
