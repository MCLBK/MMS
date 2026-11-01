import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.delivery.models import OrderStatus
from src.delivery.repository import DeliveryRepository
from src.delivery.schemas import OrderCreate, OrderUpdate, StatusTransition

VALID_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.DRAFT: {OrderStatus.PENDING, OrderStatus.CANCELLED},
    OrderStatus.PENDING: {OrderStatus.ANALYZING, OrderStatus.CANCELLED},
    OrderStatus.ANALYZING: {OrderStatus.READY_TO_ASSIGN, OrderStatus.CANCELLED},
    OrderStatus.READY_TO_ASSIGN: {OrderStatus.ASSIGNING, OrderStatus.CANCELLED},
    OrderStatus.ASSIGNING: {OrderStatus.ASSIGNED, OrderStatus.EXPIRED, OrderStatus.CANCELLED},
    OrderStatus.ASSIGNED: {
        OrderStatus.COURIER_ACCEPTED,
        OrderStatus.COURIER_REFUSED,
        OrderStatus.EXPIRED,
    },
    OrderStatus.COURIER_ACCEPTED: {OrderStatus.PICKUP_IN_PROGRESS, OrderStatus.CANCELLED},
    OrderStatus.PICKUP_IN_PROGRESS: {OrderStatus.PICKED_UP, OrderStatus.DELIVERY_FAILED},
    OrderStatus.PICKED_UP: {OrderStatus.IN_TRANSIT},
    OrderStatus.IN_TRANSIT: {OrderStatus.ARRIVING, OrderStatus.DELIVERY_FAILED},
    OrderStatus.ARRIVING: {OrderStatus.DELIVERED, OrderStatus.DELIVERY_FAILED},
    OrderStatus.DELIVERED: {OrderStatus.CONFIRMED, OrderStatus.DISPUTED},
    OrderStatus.CONFIRMED: {OrderStatus.COMPLETED},
    OrderStatus.COURIER_REFUSED: {OrderStatus.READY_TO_ASSIGN},
    OrderStatus.EXPIRED: {OrderStatus.READY_TO_ASSIGN, OrderStatus.CANCELLED},
    OrderStatus.DELIVERY_FAILED: {OrderStatus.READY_TO_ASSIGN, OrderStatus.CANCELLED},
    OrderStatus.DISPUTED: {OrderStatus.UNDER_REVIEW},
    OrderStatus.UNDER_REVIEW: {OrderStatus.RESOLVED, OrderStatus.DELIVERY_FAILED},
}


def _generate_reference() -> str:
    ts = datetime.now(UTC).strftime("%y%m%d%H%M")
    short = uuid.uuid4().hex[:6].upper()
    return f"MMS-{ts}-{short}"


class DeliveryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DeliveryRepository(db)

    async def create_order(
        self,
        data: OrderCreate,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
    ):
        if data.customer_id is None and data.new_customer is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="customer_id ou new_customer requis",
            )

        customer_id = data.customer_id
        if data.new_customer:
            customer = await self.repo.create_customer(
                {"company_id": company_id, **data.new_customer.model_dump()}
            )
            customer_id = customer.id

        existing = await self.repo.get_customer_by_id(customer_id, company_id)
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client introuvable dans cette entreprise",
            )

        reference = _generate_reference()
        while await self.repo.get_order_by_reference(reference):
            reference = _generate_reference()

        total_weight = None
        items_data = [item.model_dump() for item in data.items]
        weights = [i["weight_kg"] for i in items_data if i.get("weight_kg")]
        if weights:
            total_weight = sum(weights)

        order_data = {
            "company_id": company_id,
            "customer_id": customer_id,
            "created_by": user_id,
            "reference": reference,
            "status": OrderStatus.DRAFT,
            "priority": data.priority,
            "pickup_address": data.pickup_address,
            "pickup_lat": data.pickup_lat,
            "pickup_lng": data.pickup_lng,
            "delivery_address": data.delivery_address,
            "delivery_lat": data.delivery_lat,
            "delivery_lng": data.delivery_lng,
            "total_weight_kg": total_weight,
            "requested_delivery_at": data.requested_delivery_at,
            "special_instructions": data.special_instructions,
            "items": items_data,
        }

        order = await self.repo.create_order(order_data)
        await self.repo.add_status_history(
            order_id=order.id,
            old_status="",
            new_status=OrderStatus.DRAFT.value,
            changed_by=user_id,
        )
        return order

    async def update_order(
        self,
        order_id: uuid.UUID,
        company_id: uuid.UUID,
        data: OrderUpdate,
    ):
        order = await self.repo.get_order_by_id(order_id, company_id)
        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Commande introuvable",
            )

        if order.status not in (OrderStatus.DRAFT, OrderStatus.PENDING):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Modification impossible apres traitement",
            )

        updated = await self.repo.update_order(order, data.model_dump(exclude_unset=True))
        return updated

    async def transition_status(
        self,
        order_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        data: StatusTransition,
    ):
        order = await self.repo.get_order_by_id(order_id, company_id)
        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Commande introuvable",
            )

        allowed = VALID_TRANSITIONS.get(order.status, set())
        if data.new_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Transition {order.status.value} -> {data.new_status.value} non autorisee",
            )

        old_status = order.status.value
        order.status = data.new_status
        await self.db.flush()

        await self.repo.add_status_history(
            order_id=order.id,
            old_status=old_status,
            new_status=data.new_status.value,
            changed_by=user_id,
            reason=data.reason,
        )

        return order
