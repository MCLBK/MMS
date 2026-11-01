import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import get_db
from src.tracking.repository import TrackingRepository
from src.tracking.schemas import CourierPosition, GPSLocationCreate, GPSLocationResponse
from src.middlewares.tenant import TenantContext, resolve_tenant
from src.couriers.repository import CourierRepository

router = APIRouter()


@router.get(
    "/companies/{company_id}/tracking/live",
    response_model=list[CourierPosition],
)
async def get_live_positions(
    tenant: Annotated[TenantContext, Depends(resolve_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = TrackingRepository(db)
    profiles = await repo.get_live_positions(tenant.company_id)
    return [
        CourierPosition(
            courier_id=p.id,
            courier_name=f"{p.user.first_name} {p.user.last_name}" if p.user else "—",
            latitude=float(p.current_lat),
            longitude=float(p.current_lng),
            speed_kmh=None,
            battery_level=None,
            recorded_at=p.last_position_at.isoformat() if p.last_position_at else "",
            status=p.status.value,
        )
        for p in profiles
    ]


@router.post(
    "/companies/{company_id}/tracking/couriers/{courier_id}",
    response_model=GPSLocationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def record_gps_position(
    courier_id: uuid.UUID,
    data: GPSLocationCreate,
    tenant: Annotated[TenantContext, Depends(resolve_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    courier_repo = CourierRepository(db)
    profile = await courier_repo.get_by_id(courier_id, tenant.company_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil livreur introuvable",
        )

    await courier_repo.update_position(profile, data.latitude, data.longitude)

    tracking_repo = TrackingRepository(db)
    location = await tracking_repo.record_position(
        courier_id=courier_id,
        data=data.model_dump(exclude_none=True),
    )
    await db.commit()

    return GPSLocationResponse(
        id=location.id,
        courier_id=location.courier_id,
        latitude=float(location.latitude),
        longitude=float(location.longitude),
        accuracy_m=float(location.accuracy_m) if location.accuracy_m else None,
        speed_kmh=float(location.speed_kmh) if location.speed_kmh else None,
        heading=float(location.heading) if location.heading else None,
        battery_level=location.battery_level,
        recorded_at=location.recorded_at.isoformat(),
    )


@router.get(
    "/companies/{company_id}/tracking/couriers/{courier_id}/history",
    response_model=list[GPSLocationResponse],
)
async def get_courier_gps_history(
    courier_id: uuid.UUID,
    tenant: Annotated[TenantContext, Depends(resolve_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    minutes: int = Query(60, ge=1, le=1440),
):
    repo = TrackingRepository(db)
    locations = await repo.get_courier_history(courier_id, minutes)
    return [
        GPSLocationResponse(
            id=loc.id,
            courier_id=loc.courier_id,
            latitude=float(loc.latitude),
            longitude=float(loc.longitude),
            accuracy_m=float(loc.accuracy_m) if loc.accuracy_m else None,
            speed_kmh=float(loc.speed_kmh) if loc.speed_kmh else None,
            heading=float(loc.heading) if loc.heading else None,
            battery_level=loc.battery_level,
            recorded_at=loc.recorded_at.isoformat(),
        )
        for loc in locations
    ]
