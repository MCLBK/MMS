import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.companies.models import Company


class CompanyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, company_id: uuid.UUID) -> Company | None:
        result = await self.db.execute(select(Company).where(Company.id == company_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Company | None:
        result = await self.db.execute(select(Company).where(Company.slug == slug))
        return result.scalar_one_or_none()

    async def list_companies(self, offset: int = 0, limit: int = 20) -> tuple[list[Company], int]:
        count_stmt = select(func.count()).select_from(Company)
        total = (await self.db.execute(count_stmt)).scalar() or 0

        stmt = (
            select(Company)
            .order_by(Company.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def create(self, data: dict) -> Company:
        company = Company(**data)
        self.db.add(company)
        await self.db.flush()
        return company

    async def update(self, company: Company, data: dict) -> Company:
        for key, value in data.items():
            if value is not None:
                setattr(company, key, value)
        await self.db.flush()
        return company
