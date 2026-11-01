"""Configuration des fixtures de test.

Utilise une base SQLite en mémoire pour les tests unitaires,
ce qui évite de dépendre de PostgreSQL pour le CI.
"""

import os
import uuid
from datetime import UTC, datetime

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database.base import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

_test_engine = None
_test_session_factory = None


def get_test_engine():
    global _test_engine
    if _test_engine is None:
        _test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    return _test_engine


@pytest.fixture
async def db_session():
    global _test_session_factory
    engine = get_test_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if _test_session_factory is None:
        _test_session_factory = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

    async with _test_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client():
    from src.database.base import get_db
    from src.main import app

    async def override_get_db():
        yield None

    app.dependency_overrides[get_db] = override_get_db

    from httpx import ASGITransport, AsyncClient

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


def make_uuid() -> uuid.UUID:
    return uuid.uuid4()


def utcnow() -> datetime:
    return datetime.now(UTC)
