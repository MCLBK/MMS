"""Service d'attribution automatique des commandes aux livreurs.

Utilise le scoring IA avancé (v2) pour évaluer et classer les candidats.
"""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.scoring import AIScoring
from src.couriers.repository import CourierRepository
from src.delivery.models import (
    AssignmentStatus,
    DeliveryAssignment,
    OrderStatus,
)
from src.delivery.repository import DeliveryRepository


class AssignmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.courier_repo = CourierRepository(db)
        self.delivery_repo = DeliveryRepository(db)
        self.scoring = AIScoring(db)

    async def auto_assign(
        self, order_id: uuid.UUID, company_id: uuid.UUID
    ) -> DeliveryAssignment | None:
        order = await self.delivery_repo.get_order_by_id(order_id, company_id)
        if order is None or order.status != OrderStatus.READY_TO_ASSIGN:
            return None

        available = await self.courier_repo.get_available_couriers(company_id)
        if not available:
            return None

        candidates = await self.scoring.score_candidates(order, available)
        if not candidates:
            return None

        best = candidates[0]

        now = datetime.now(timezone.utc)
        assignment = DeliveryAssignment(
            order_id=order.id,
            courier_id=best.courier.id,
            status=AssignmentStatus.PENDING,
            assigned_at=now,
            expires_at=now + timedelta(minutes=10),
            ai_score=best.factors.total_score,
            ai_reasoning=self.scoring.factors_to_dict(best.factors),
        )
        self.db.add(assignment)

        order.status = OrderStatus.ASSIGNED
        await self.db.flush()

        await self.delivery_repo.add_status_history(
            order_id=order.id,
            old_status=OrderStatus.READY_TO_ASSIGN.value,
            new_status=OrderStatus.ASSIGNED.value,
        )

        return assignment
