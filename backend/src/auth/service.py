from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from src.users.models import User


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: RegisterRequest) -> User:
        existing = await self.db.execute(select(User).where(User.email == data.email))
        if existing.scalar_one_or_none() is not None:
            raise ValueError("Un compte avec cet email existe deja")

        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            is_active=True,
            is_verified=False,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def login(self, data: LoginRequest) -> TokenResponse:
        stmt = select(User).where(User.email == data.email, User.is_active.is_(True))
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None or not verify_password(data.password, user.password_hash):
            raise ValueError("Email ou mot de passe incorrect")

        user.last_login_at = datetime.now(timezone.utc)
        await self.db.flush()

        token_data = {"sub": str(user.id), "email": user.email}
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise ValueError("Refresh token invalide")

        user_id = payload.get("sub")
        stmt = select(User).where(User.id == user_id, User.is_active.is_(True))
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise ValueError("Utilisateur introuvable")

        token_data = {"sub": str(user.id), "email": user.email}
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        )
