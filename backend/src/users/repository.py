import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.users.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = select(User).options(selectinload(User.memberships)).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def list_users(self, offset: int = 0, limit: int = 20) -> tuple[list[User], int]:
        count_stmt = select(func.count()).select_from(User)
        total = (await self.db.execute(count_stmt)).scalar() or 0

        stmt = (
            select(User)
            .options(selectinload(User.memberships))
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def update(self, user: User, data: dict) -> User:
        for key, value in data.items():
            if value is not None:
                setattr(user, key, value)
        await self.db.flush()
        return user
