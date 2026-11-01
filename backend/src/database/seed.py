"""Seed initial roles, permissions, and the first super admin."""

from datetime import datetime, timezone

from sqlalchemy import select

from src.core.config import settings
from src.core.security import hash_password
from src.database.base import async_session
from src.users.models import CompanyMembership, Permission, Role, SystemRole, User, role_permissions


PERMISSIONS = [
    ("users", "read"), ("users", "create"), ("users", "update"), ("users", "delete"),
    ("companies", "read"), ("companies", "create"), ("companies", "update"), ("companies", "delete"),
    ("orders", "read"), ("orders", "create"), ("orders", "update"), ("orders", "delete"),
    ("couriers", "read"), ("couriers", "create"), ("couriers", "update"), ("couriers", "delete"),
    ("assignments", "read"), ("assignments", "create"), ("assignments", "update"),
    ("tracking", "read"), ("tracking", "create"),
    ("analytics", "read"),
    ("notifications", "read"), ("notifications", "create"),
    ("audit", "read"),
    ("chat", "read"), ("chat", "create"),
    ("settings", "read"), ("settings", "update"),
]

ROLE_PERMS = {
    SystemRole.SUPER_ADMIN: "*",
    SystemRole.COMPANY_ADMIN: [
        ("users", "read"), ("users", "create"), ("users", "update"),
        ("companies", "read"), ("companies", "update"),
        ("orders", "read"), ("orders", "create"), ("orders", "update"), ("orders", "delete"),
        ("couriers", "read"), ("couriers", "create"), ("couriers", "update"),
        ("assignments", "read"), ("assignments", "create"), ("assignments", "update"),
        ("tracking", "read"),
        ("analytics", "read"),
        ("notifications", "read"), ("notifications", "create"),
        ("chat", "read"), ("chat", "create"),
        ("settings", "read"), ("settings", "update"),
    ],
    SystemRole.COURIER: [
        ("orders", "read"),
        ("assignments", "read"), ("assignments", "update"),
        ("tracking", "read"), ("tracking", "create"),
        ("notifications", "read"),
        ("chat", "read"), ("chat", "create"),
    ],
    SystemRole.CUSTOMER: [
        ("orders", "read"),
        ("tracking", "read"),
        ("notifications", "read"),
        ("chat", "read"), ("chat", "create"),
    ],
}


async def seed_roles_and_admin() -> None:
    async with async_session() as session:
        existing = await session.execute(select(Role).limit(1))
        if existing.scalar_one_or_none() is not None:
            return

        perm_map: dict[tuple[str, str], Permission] = {}
        for resource, action in PERMISSIONS:
            p = Permission(resource=resource, action=action, description=f"{action} {resource}")
            session.add(p)
            perm_map[(resource, action)] = p

        await session.flush()

        for role_name in SystemRole:
            role = Role(name=role_name.value, description=role_name.value.replace("_", " ").title(), is_system=True)
            session.add(role)
            await session.flush()

            perms = ROLE_PERMS[role_name]
            if perms == "*":
                role.permissions = list(perm_map.values())
            else:
                role.permissions = [perm_map[key] for key in perms if key in perm_map]

        await session.flush()

        admin_role = await session.execute(
            select(Role).where(Role.name == SystemRole.SUPER_ADMIN.value)
        )
        admin_role = admin_role.scalar_one()

        admin = User(
            email=settings.FIRST_ADMIN_EMAIL,
            password_hash=hash_password(settings.FIRST_ADMIN_PASSWORD),
            first_name="Admin",
            last_name="MMS",
            is_active=True,
            is_verified=True,
            global_role_id=admin_role.id,
        )
        session.add(admin)

        await session.commit()
