"""RBAC decorators and dependency factories for route protection."""

import uuid
from functools import wraps
from typing import Annotated

from fastapi import Depends, HTTPException, status

from src.core.dependencies import get_current_active_user
from src.users.models import SystemRole, User


def require_role(*roles: str):
    """Dependency that checks if the current user has one of the required roles."""

    async def _check(
        current_user: Annotated[User, Depends(get_current_active_user)],
        company_id: uuid.UUID | None = None,
    ) -> User:
        if current_user.is_super_admin:
            return current_user

        for role_name in roles:
            if current_user.has_role(role_name, company_id):
                return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes",
        )

    return _check


def require_permission(resource: str, action: str):
    """Dependency that checks if the current user has a specific permission."""

    async def _check(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if current_user.is_super_admin:
            return current_user

        if current_user.global_role:
            for perm in current_user.global_role.permissions:
                if perm.resource == resource and perm.action == action:
                    return current_user

        for membership in current_user.memberships:
            if membership.role:
                for perm in membership.role.permissions:
                    if perm.resource == resource and perm.action == action:
                        return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission requise : {action} {resource}",
        )

    return _check


def require_super_admin():
    """Dependency that restricts access to super admins only."""

    async def _check(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if not current_user.is_super_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acces reserve aux super administrateurs",
            )
        return current_user

    return _check
