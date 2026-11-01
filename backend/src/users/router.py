import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_current_active_user
from src.database.base import get_db
from src.guards.rbac import require_permission
from src.users.models import User
from src.users.repository import UserRepository
from src.users.schemas import UserDetail, UserListItem, UserUpdate

router = APIRouter()


@router.get("/", response_model=list[UserListItem])
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[User, Depends(require_permission("users", "read"))],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    repo = UserRepository(db)
    users, total = await repo.list_users(offset=(page - 1) * page_size, limit=page_size)
    return [
        UserListItem(
            id=u.id,
            email=u.email,
            first_name=u.first_name,
            last_name=u.last_name,
            phone=u.phone,
            is_active=u.is_active,
            is_verified=u.is_verified,
            is_super_admin=u.is_super_admin,
        )
        for u in users
    ]


@router.get("/{user_id}", response_model=UserDetail)
async def get_user(
    user_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[User, Depends(require_permission("users", "read"))],
):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")

    memberships = []
    for m in user.memberships:
        memberships.append({
            "company_id": m.company_id,
            "company_name": m.company.name if m.company else "",
            "role_name": m.role.name if m.role else "",
            "is_active": m.is_active,
        })

    return UserDetail(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        is_verified=user.is_verified,
        is_super_admin=user.is_super_admin,
        created_at=user.created_at.isoformat(),
        memberships=memberships,
    )


@router.patch("/{user_id}", response_model=UserListItem)
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[User, Depends(require_permission("users", "update"))],
):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")

    updated = await repo.update(user, data.model_dump(exclude_unset=True))
    return UserListItem(
        id=updated.id,
        email=updated.email,
        first_name=updated.first_name,
        last_name=updated.last_name,
        phone=updated.phone,
        is_active=updated.is_active,
        is_verified=updated.is_verified,
        is_super_admin=updated.is_super_admin,
    )
