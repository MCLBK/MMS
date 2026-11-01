import uuid
from typing import Annotated
import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import get_db
from src.delivery.models import OrderStatus
from src.delivery.schemas import (
    CustomerCreate,
    CustomerResponse,
    OrderCreate,
    OrderDetail,
    OrderListItem,
    OrderUpdate,
    PaginatedOrders,
    StatusTransition,
)
from src.delivery.service import DeliveryService
from src.delivery.repository import DeliveryRepository
from src.guards.rbac import require_permission
from src.middlewares.tenant import TenantContext, resolve_tenant
from src.users.models import User

router = APIRouter()


def _order_to_list_item(order) -> OrderListItem:
    return OrderListItem(
        id=order.id,
        reference=order.reference,
        status=order.status,
        priority=order.priority,
        customer_name=order.customer.name if order.customer else "—",
        pickup_address=order.pickup_address,
        delivery_address=order.delivery_address,
        created_at=order.created_at.isoformat(),
    )


def _order_to_detail(order) -> OrderDetail:
    return OrderDetail(
        id=order.id,
        reference=order.reference,
        status=order.status,
        priority=order.priority,
        pickup_address=order.pickup_address,
        pickup_lat=float(order.pickup_lat) if order.pickup_lat else None,
        pickup_lng=float(order.pickup_lng) if order.pickup_lng else None,
        delivery_address=order.delivery_address,
        delivery_lat=float(order.delivery_lat) if order.delivery_lat else None,
        delivery_lng=float(order.delivery_lng) if order.delivery_lng else None,
        total_weight_kg=float(order.total_weight_kg) if order.total_weight_kg else None,
        estimated_distance_km=float(order.estimated_distance_km) if order.estimated_distance_km else None,
        estimated_duration_min=order.estimated_duration_min,
        requested_delivery_at=order.requested_delivery_at.isoformat() if order.requested_delivery_at else None,
        special_instructions=order.special_instructions,
        customer=CustomerResponse.model_validate(order.customer),
        items=[item for item in order.items],
        created_at=order.created_at.isoformat(),
        updated_at=order.updated_at.isoformat(),
    )


# ── Orders ────────────────────────────────────────────────────

@router.get(
    "/companies/{company_id}/orders",
    response_model=PaginatedOrders,
)
async def list_orders(
    tenant: Annotated[TenantContext, Depends(resolve_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: OrderStatus | None = Query(None, alias="status"),
    search: str | None = Query(None),
):
    repo = DeliveryRepository(db)
    orders, total = await repo.list_orders(
        company_id=tenant.company_id,
        offset=(page - 1) * page_size,
        limit=page_size,
        status_filter=status_filter,
        search=search,
    )
    return PaginatedOrders(
        items=[_order_to_list_item(o) for o in orders],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, math.ceil(total / page_size)),
    )


@router.post(
    "/companies/{company_id}/orders",
    response_model=OrderDetail,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    data: OrderCreate,
    tenant: Annotated[TenantContext, Depends(resolve_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = DeliveryService(db)
    order = await service.create_order(
        data=data,
        company_id=tenant.company_id,
        user_id=tenant.user.id,
    )
    await db.commit()
    refreshed = await DeliveryRepository(db).get_order_by_id(order.id, tenant.company_id)
    return _order_to_detail(refreshed)


@router.get(
    "/companies/{company_id}/orders/{order_id}",
    response_model=OrderDetail,
)
async def get_order(
    order_id: uuid.UUID,
    tenant: Annotated[TenantContext, Depends(resolve_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = DeliveryRepository(db)
    order = await repo.get_order_by_id(order_id, tenant.company_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commande introuvable",
        )
    return _order_to_detail(order)


@router.patch(
    "/companies/{company_id}/orders/{order_id}",
    response_model=OrderDetail,
)
async def update_order(
    order_id: uuid.UUID,
    data: OrderUpdate,
    tenant: Annotated[TenantContext, Depends(resolve_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = DeliveryService(db)
    order = await service.update_order(order_id, tenant.company_id, data)
    await db.commit()
    refreshed = await DeliveryRepository(db).get_order_by_id(order.id, tenant.company_id)
    return _order_to_detail(refreshed)


@router.post(
    "/companies/{company_id}/orders/{order_id}/transition",
    response_model=OrderDetail,
)
async def transition_order_status(
    order_id: uuid.UUID,
    data: StatusTransition,
    tenant: Annotated[TenantContext, Depends(resolve_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = DeliveryService(db)
    order = await service.transition_status(
        order_id, tenant.company_id, tenant.user.id, data
    )
    await db.commit()
    refreshed = await DeliveryRepository(db).get_order_by_id(order.id, tenant.company_id)
    return _order_to_detail(refreshed)


# ── Customers ─────────────────────────────────────────────────

@router.get(
    "/companies/{company_id}/customers",
    response_model=list[CustomerResponse],
)
async def list_customers(
    tenant: Annotated[TenantContext, Depends(resolve_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    repo = DeliveryRepository(db)
    customers, _ = await repo.list_customers(
        tenant.company_id, offset=(page - 1) * page_size, limit=page_size
    )
    return [CustomerResponse.model_validate(c) for c in customers]


@router.post(
    "/companies/{company_id}/customers",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_customer(
    data: CustomerCreate,
    tenant: Annotated[TenantContext, Depends(resolve_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = DeliveryRepository(db)
    customer = await repo.create_customer(
        {"company_id": tenant.company_id, **data.model_dump()}
    )
    await db.commit()
    return CustomerResponse.model_validate(customer)


# ── Auto-assign ───────────────────────────────────────────────

@router.post(
    "/companies/{company_id}/orders/{order_id}/assign",
    status_code=status.HTTP_200_OK,
)
async def auto_assign_order(
    order_id: uuid.UUID,
    tenant: Annotated[TenantContext, Depends(resolve_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    from src.delivery.assignment_service import AssignmentService

    service = AssignmentService(db)
    assignment = await service.auto_assign(order_id, tenant.company_id)
    if assignment is None:
        from fastapi import HTTPException as HE

        raise HE(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attribution impossible : aucun livreur disponible ou statut invalide",
        )
    await db.commit()
    return {
        "status": "assigned",
        "courier_id": str(assignment.courier_id),
        "score": float(assignment.ai_score) if assignment.ai_score else None,
        "expires_at": assignment.expires_at.isoformat(),
    }
