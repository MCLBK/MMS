import math
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import get_db
from src.guards.rbac import require_super_admin
from src.middlewares.tenant import TenantContext, resolve_tenant
from src.schemas.audit_schemas import AuditLogResponse, PaginatedAuditLogs
from src.schemas.audit_service import AuditService
from src.users.models import User

router = APIRouter()


@router.get(
    "/companies/{company_id}/audit",
    response_model=PaginatedAuditLogs,
)
async def list_company_audit_logs(
    tenant: Annotated[TenantContext, Depends(resolve_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    action: str | None = Query(None),
    resource_type: str | None = Query(None),
):
    service = AuditService(db)
    logs, total = await service.list_logs(
        company_id=tenant.company_id,
        offset=(page - 1) * page_size,
        limit=page_size,
        action_filter=action,
        resource_type_filter=resource_type,
    )
    return PaginatedAuditLogs(
        items=[
            AuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                company_id=log.company_id,
                action=log.action,
                resource_type=log.resource_type,
                resource_id=log.resource_id,
                details=log.details,
                ip_address=log.ip_address,
                created_at=log.created_at.isoformat(),
            )
            for log in logs
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/audit", response_model=PaginatedAuditLogs)
async def list_global_audit_logs(
    _user: Annotated[User, Depends(require_super_admin())],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    action: str | None = Query(None),
    resource_type: str | None = Query(None),
):
    service = AuditService(db)
    logs, total = await service.list_logs(
        offset=(page - 1) * page_size,
        limit=page_size,
        action_filter=action,
        resource_type_filter=resource_type,
    )
    return PaginatedAuditLogs(
        items=[
            AuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                company_id=log.company_id,
                action=log.action,
                resource_type=log.resource_type,
                resource_id=log.resource_id,
                details=log.details,
                ip_address=log.ip_address,
                created_at=log.created_at.isoformat(),
            )
            for log in logs
        ],
        total=total,
        page=page,
        page_size=page_size,
    )
