import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import case, cast, Date, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.delivery.models import CourierProfile, CourierStatus, DeliveryOrder, OrderStatus
from src.analytics.schemas import (
    CourierPerformance,
    DailyStats,
    DashboardStats,
    OrdersByStatus,
)


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_stats(self, company_id: uuid.UUID) -> DashboardStats:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        base = select(DeliveryOrder).where(DeliveryOrder.company_id == company_id)

        total = (await self.db.execute(
            select(func.count()).select_from(base.subquery())
        )).scalar() or 0

        today_orders = (await self.db.execute(
            select(func.count()).select_from(
                base.where(DeliveryOrder.created_at >= today_start).subquery()
            )
        )).scalar() or 0

        in_transit = (await self.db.execute(
            select(func.count()).select_from(
                base.where(DeliveryOrder.status.in_([
                    OrderStatus.IN_TRANSIT, OrderStatus.ARRIVING,
                    OrderStatus.PICKUP_IN_PROGRESS, OrderStatus.PICKED_UP,
                ])).subquery()
            )
        )).scalar() or 0

        completed_today = (await self.db.execute(
            select(func.count()).select_from(
                base.where(
                    DeliveryOrder.status == OrderStatus.COMPLETED,
                    DeliveryOrder.updated_at >= today_start,
                ).subquery()
            )
        )).scalar() or 0

        pending = (await self.db.execute(
            select(func.count()).select_from(
                base.where(DeliveryOrder.status.in_([
                    OrderStatus.PENDING, OrderStatus.ANALYZING,
                    OrderStatus.READY_TO_ASSIGN, OrderStatus.ASSIGNING,
                ])).subquery()
            )
        )).scalar() or 0

        failed = (await self.db.execute(
            select(func.count()).select_from(
                base.where(DeliveryOrder.status == OrderStatus.DELIVERY_FAILED).subquery()
            )
        )).scalar() or 0

        courier_base = select(CourierProfile).where(CourierProfile.company_id == company_id)
        total_couriers = (await self.db.execute(
            select(func.count()).select_from(
                courier_base.where(CourierProfile.is_active.is_(True)).subquery()
            )
        )).scalar() or 0

        available_couriers = (await self.db.execute(
            select(func.count()).select_from(
                courier_base.where(
                    CourierProfile.is_active.is_(True),
                    CourierProfile.status == CourierStatus.AVAILABLE,
                ).subquery()
            )
        )).scalar() or 0

        completed_total = (await self.db.execute(
            select(func.count()).select_from(
                base.where(DeliveryOrder.status == OrderStatus.COMPLETED).subquery()
            )
        )).scalar() or 0

        completion_rate = (completed_total / total * 100) if total > 0 else None

        return DashboardStats(
            total_orders=total,
            orders_today=today_orders,
            in_transit=in_transit,
            completed_today=completed_today,
            pending=pending,
            failed=failed,
            total_couriers=total_couriers,
            available_couriers=available_couriers,
            avg_delivery_time_min=None,
            completion_rate=round(completion_rate, 1) if completion_rate else None,
        )

    async def get_orders_by_status(self, company_id: uuid.UUID) -> list[OrdersByStatus]:
        stmt = (
            select(DeliveryOrder.status, func.count().label("count"))
            .where(DeliveryOrder.company_id == company_id)
            .group_by(DeliveryOrder.status)
        )
        result = await self.db.execute(stmt)
        return [
            OrdersByStatus(status=row.status.value, count=row.count)
            for row in result.all()
        ]

    async def get_daily_stats(
        self, company_id: uuid.UUID, days: int = 7
    ) -> list[DailyStats]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        date_col = cast(DeliveryOrder.created_at, Date)

        stmt = (
            select(
                date_col.label("date"),
                func.count().label("created"),
                func.sum(case(
                    (DeliveryOrder.status == OrderStatus.COMPLETED, 1), else_=0
                )).label("completed"),
                func.sum(case(
                    (DeliveryOrder.status == OrderStatus.DELIVERY_FAILED, 1), else_=0
                )).label("failed"),
            )
            .where(
                DeliveryOrder.company_id == company_id,
                DeliveryOrder.created_at >= since,
            )
            .group_by(date_col)
            .order_by(date_col)
        )
        result = await self.db.execute(stmt)
        return [
            DailyStats(
                date=row.date.isoformat(),
                created=row.created,
                completed=row.completed or 0,
                failed=row.failed or 0,
            )
            for row in result.all()
        ]

    async def get_courier_performance(
        self, company_id: uuid.UUID
    ) -> list[CourierPerformance]:
        from src.delivery.models import DeliveryAssignment, AssignmentStatus

        stmt = (
            select(
                CourierProfile.id,
                CourierProfile.rating,
                CourierProfile.total_deliveries,
                func.count(DeliveryAssignment.id).label("assigned"),
                func.sum(case(
                    (DeliveryAssignment.status == AssignmentStatus.COMPLETED, 1), else_=0
                )).label("done"),
                func.sum(case(
                    (DeliveryAssignment.status == AssignmentStatus.FAILED, 1), else_=0
                )).label("fail"),
            )
            .join(CourierProfile.user)
            .outerjoin(DeliveryAssignment, DeliveryAssignment.courier_id == CourierProfile.id)
            .where(CourierProfile.company_id == company_id, CourierProfile.is_active.is_(True))
            .group_by(CourierProfile.id)
            .order_by(CourierProfile.total_deliveries.desc())
            .limit(20)
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        out = []
        for row in rows:
            profile = row[0]
            done = row[4] or 0
            fail = row[5] or 0
            total = done + fail
            out.append(CourierPerformance(
                courier_id=str(profile),
                courier_name="",
                total_deliveries=row[3] or 0,
                completed=done,
                failed=fail,
                avg_rating=float(row[1]),
                completion_rate=round(done / total * 100, 1) if total > 0 else 0,
            ))
        return out
