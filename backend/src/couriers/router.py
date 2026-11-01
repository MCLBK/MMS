import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.couriers.repository import CourierRepository
from src.couriers.schemas import (
    CourierDetail,
    CourierListItem,
    CourierPositionUpdate,
    CourierProfileCreate,
    CourierProfileUpdate,
)
from src.database.base import get_db
from src.delivery.models import CourierStatus
from src.middlewares.tenant import TenantContext, resolve_tenant

router = APIRouter()


def _to_list_item(c) -> CourierListItem:
    return CourierListItem(
        id=c.id,
        user_name=f"{c.user.first_name} {c.user.last_name}" if c.user else "—",
        vehicle_type=c.vehicle_type,
        status=c.status,
        rating=float(c.rating),
        total_deliveries=c.total_deliveries,
        is_active=c.is_active,
    )


def _to_detail(c) -> CourierDetail:
    return CourierDetail(
        id=c.id,
        user_id=c.user_id,
        user_name=f"{c.user.first_name} {c.user.last_name}" if c.user else "—",
        user_email=c.user.email if c.user else "",
        vehicle_type=c.vehicle_type,
        max_weight_kg=float(c.max_weight_kg),
        max_volume_m3=float(c.max_volume_m3),
        license_number=c.license_number,
        status=c.status,
        current_lat=float(c.current_lat) if c.current_lat else None,
        current_lng=float(c.current_lng) if c.current_lng else None,
        last_position_at=c.last_position_at.isoformat() if c.last_position_at else None,
        rating=float(c.rating),
        total_deliveries=c.total_deliveries,
        is_active=c.is_active,
        created_at=c.created_at.isoformat(),
    )


@router.get(
    "/companies/{company_id}/couriers",
    response_model=list[CourierListItem],
)
async def list_couriers(
    tenant: Annotated[TenantContext, Depends(resolve_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    courier_status: CourierStatus | None = Query(None, alias="status"),
    active_only: bool = Query(False),
):
    repo = CourierRepository(db)
    couriers, _ = await repo.list_couriers(
        company_id=tenant.company_id,
        offset=(page - 1) * page_size,
        limit=page_size,
        status_filter=courier_status,
        active_only=active_only,
    )
    return [_to_list_item(c) for c in couriers]


@router.post(
    "/companies/{company_id}/couriers",
    response_model=CourierDetail,
    status_code=status.HTTP_201_CREATED,
)
async def create_courier_profile(
    data: CourierProfileCreate,
    tenant: Annotated[TenantContext, Depends(resolve_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = CourierRepository(db)
    existing = await repo.get_by_user_id(data.user_id, tenant.company_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce livreur a deja un profil dans cette entreprise",
        )

    profile = await repo.create(
        {
            "company_id": tenant.company_id,
            **data.model_dump(),
        }
    )
    await db.commit()
    refreshed = await repo.get_by_id(profile.id, tenant.company_id)
    return _to_detail(refreshed)


@router.get(
    "/companies/{company_id}/couriers/{courier_id}",
    response_model=CourierDetail,
)
async def get_courier(
    courier_id: uuid.UUID,
    tenant: Annotated[TenantContext, Depends(resolve_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = CourierRepository(db)
    profile = await repo.get_by_id(courier_id, tenant.company_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil livreur introuvable",
        )
    return _to_detail(profile)


@router.patch(
    "/companies/{company_id}/couriers/{courier_id}",
    response_model=CourierDetail,
)
async def update_courier_profile(
    courier_id: uuid.UUID,
    data: CourierProfileUpdate,
    tenant: Annotated[TenantContext, Depends(resolve_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = CourierRepository(db)
    profile = await repo.get_by_id(courier_id, tenant.company_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil livreur introuvable",
        )

    updated = await repo.update(profile, data.model_dump(exclude_unset=True))
    await db.commit()
    refreshed = await repo.get_by_id(updated.id, tenant.company_id)
    return _to_detail(refreshed)


@router.post(
    "/companies/{company_id}/couriers/{courier_id}/position",
    response_model=CourierDetail,
)
async def update_courier_position(
    courier_id: uuid.UUID,
    data: CourierPositionUpdate,
    tenant: Annotated[TenantContext, Depends(resolve_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = CourierRepository(db)
    profile = await repo.get_by_id(courier_id, tenant.company_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil livreur introuvable",
        )

    updated = await repo.update_position(profile, data.latitude, data.longitude)
    await db.commit()
    refreshed = await repo.get_by_id(updated.id, tenant.company_id)
    return _to_detail(refreshed)
