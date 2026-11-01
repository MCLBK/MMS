import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.analytics.schemas import DailyStats, DashboardStats, OrdersByStatus
from src.analytics.service import AnalyticsService
from src.database.base import get_db
from src.middlewares.tenant import TenantContext, resolve_tenant

router = APIRouter()


@router.get(
    "/companies/{company_id}/analytics/dashboard",
    response_model=DashboardStats,
)
async def dashboard_stats(
    tenant: Annotated[TenantContext, Depends(resolve_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AnalyticsService(db)
    return await service.get_dashboard_stats(tenant.company_id)


@router.get(
    "/companies/{company_id}/analytics/orders-by-status",
    response_model=list[OrdersByStatus],
)
async def orders_by_status(
    tenant: Annotated[TenantContext, Depends(resolve_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AnalyticsService(db)
    return await service.get_orders_by_status(tenant.company_id)


@router.get(
    "/companies/{company_id}/analytics/daily",
    response_model=list[DailyStats],
)
async def daily_stats(
    tenant: Annotated[TenantContext, Depends(resolve_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    days: int = Query(7, ge=1, le=90),
):
    service = AnalyticsService(db)
    return await service.get_daily_stats(tenant.company_id, days)
