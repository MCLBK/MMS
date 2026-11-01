"""Multi-tenant middleware and helpers.

Every query that accesses tenant-scoped data must filter by company_id.
This module provides utilities to enforce that at the repository level.
"""

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.companies.models import Company
from src.core.dependencies import get_current_active_user
from src.database.base import get_db
from src.users.models import User


class TenantContext:
    """Holds the resolved company for the current request."""

    def __init__(self, company: Company, user: User):
        self.company = company
        self.user = user
        self.company_id = company.id


async def resolve_tenant(
    company_id: Annotated[uuid.UUID, Path(description="ID de l'entreprise")],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TenantContext:
    """Resolve and authorize tenant access.

    Super admins can access any company.
    Other users can only access companies they belong to.
    """
    result = await db.execute(
        select(Company).where(Company.id == company_id, Company.is_active.is_(True))
    )
    company = result.scalar_one_or_none()

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entreprise introuvable",
        )

    if current_user.is_super_admin:
        return TenantContext(company=company, user=current_user)

    user_company_ids = {m.company_id for m in current_user.memberships if m.is_active}
    if company_id not in user_company_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acces refuse a cette entreprise",
        )

    return TenantContext(company=company, user=current_user)
