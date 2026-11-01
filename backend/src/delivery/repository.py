import uuid
from datetime import UTC

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.delivery.models import (
    Customer,
    DeliveryItem,
    DeliveryOrder,
    DeliveryStatusHistory,
    OrderStatus,
)


class DeliveryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Orders ────────────────────────────────────────────────

    async def get_order_by_id(
        self, order_id: uuid.UUID, company_id: uuid.UUID
    ) -> DeliveryOrder | None:
        stmt = (
            select(DeliveryOrder)
            .options(
                selectinload(DeliveryOrder.customer),
                selectinload(DeliveryOrder.items),
            )
            .where(DeliveryOrder.id == order_id, DeliveryOrder.company_id == company_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_order_by_reference(self, reference: str) -> DeliveryOrder | None:
        result = await self.db.execute(
            select(DeliveryOrder).where(DeliveryOrder.reference == reference)
        )
        return result.scalar_one_or_none()

    async def list_orders(
        self,
        company_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        status_filter: OrderStatus | None = None,
        search: str | None = None,
    ) -> tuple[list[DeliveryOrder], int]:
        base = select(DeliveryOrder).where(DeliveryOrder.company_id == company_id)

        if status_filter:
            base = base.where(DeliveryOrder.status == status_filter)
        if search:
            pattern = f"%{search}%"
            base = base.where(
                DeliveryOrder.reference.ilike(pattern)
                | DeliveryOrder.pickup_address.ilike(pattern)
                | DeliveryOrder.delivery_address.ilike(pattern)
            )

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.db.execute(count_stmt)).scalar() or 0

        stmt = (
            base.options(selectinload(DeliveryOrder.customer))
            .order_by(DeliveryOrder.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def create_order(self, data: dict) -> DeliveryOrder:
        items_data = data.pop("items", [])
        order = DeliveryOrder(**data)
        self.db.add(order)
        await self.db.flush()

        for item_data in items_data:
            item = DeliveryItem(order_id=order.id, **item_data)
            self.db.add(item)
        await self.db.flush()

        return await self.get_order_by_id(order.id, order.company_id)

    async def update_order(self, order: DeliveryOrder, data: dict) -> DeliveryOrder:
        for key, value in data.items():
            if value is not None:
                setattr(order, key, value)
        await self.db.flush()
        return order

    # ── Status History ────────────────────────────────────────

    async def add_status_history(
        self,
        order_id: uuid.UUID,
        old_status: str,
        new_status: str,
        changed_by: uuid.UUID | None = None,
        reason: str | None = None,
    ) -> DeliveryStatusHistory:
        from datetime import datetime

        entry = DeliveryStatusHistory(
            order_id=order_id,
            changed_by=changed_by,
            old_status=old_status,
            new_status=new_status,
            reason=reason,
            created_at=datetime.now(UTC),
        )
        self.db.add(entry)
        await self.db.flush()
        return entry

    # ── Customers ─────────────────────────────────────────────

    async def get_customer_by_id(
        self, customer_id: uuid.UUID, company_id: uuid.UUID
    ) -> Customer | None:
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id, Customer.company_id == company_id)
        )
        return result.scalar_one_or_none()

    async def create_customer(self, data: dict) -> Customer:
        customer = Customer(**data)
        self.db.add(customer)
        await self.db.flush()
        return customer

    async def list_customers(
        self, company_id: uuid.UUID, offset: int = 0, limit: int = 50
    ) -> tuple[list[Customer], int]:
        base = select(Customer).where(Customer.company_id == company_id)
        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.db.execute(count_stmt)).scalar() or 0

        stmt = base.order_by(Customer.name).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total
