import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.companies.repository import CompanyRepository
from src.companies.schemas import CompanyCreate, CompanyDetail, CompanyListItem, CompanyUpdate
from src.database.base import get_db
from src.guards.rbac import require_permission, require_super_admin
from src.users.models import User

router = APIRouter()


@router.get("/", response_model=list[CompanyListItem])
async def list_companies(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[User, Depends(require_permission("companies", "read"))],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    repo = CompanyRepository(db)
    companies, _ = await repo.list_companies(offset=(page - 1) * page_size, limit=page_size)
    return [
        CompanyListItem(
            id=c.id, name=c.name, slug=c.slug, city=c.city, country=c.country, is_active=c.is_active
        )
        for c in companies
    ]


@router.post("/", response_model=CompanyDetail, status_code=status.HTTP_201_CREATED)
async def create_company(
    data: CompanyCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[User, Depends(require_super_admin())],
):
    repo = CompanyRepository(db)
    existing = await repo.get_by_slug(data.slug)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce slug est deja utilise")

    company = await repo.create(data.model_dump())
    return CompanyDetail(
        id=company.id,
        name=company.name,
        slug=company.slug,
        address=company.address,
        city=company.city,
        country=company.country,
        latitude=float(company.latitude) if company.latitude else None,
        longitude=float(company.longitude) if company.longitude else None,
        phone=company.phone,
        email=company.email,
        logo_url=company.logo_url,
        is_active=company.is_active,
        created_at=company.created_at.isoformat(),
    )


@router.get("/{company_id}", response_model=CompanyDetail)
async def get_company(
    company_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[User, Depends(require_permission("companies", "read"))],
):
    repo = CompanyRepository(db)
    company = await repo.get_by_id(company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entreprise introuvable")

    return CompanyDetail(
        id=company.id,
        name=company.name,
        slug=company.slug,
        address=company.address,
        city=company.city,
        country=company.country,
        latitude=float(company.latitude) if company.latitude else None,
        longitude=float(company.longitude) if company.longitude else None,
        phone=company.phone,
        email=company.email,
        logo_url=company.logo_url,
        is_active=company.is_active,
        created_at=company.created_at.isoformat(),
    )


@router.patch("/{company_id}", response_model=CompanyDetail)
async def update_company(
    company_id: uuid.UUID,
    data: CompanyUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[User, Depends(require_permission("companies", "update"))],
):
    repo = CompanyRepository(db)
    company = await repo.get_by_id(company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entreprise introuvable")

    updated = await repo.update(company, data.model_dump(exclude_unset=True))
    return CompanyDetail(
        id=updated.id,
        name=updated.name,
        slug=updated.slug,
        address=updated.address,
        city=updated.city,
        country=updated.country,
        latitude=float(updated.latitude) if updated.latitude else None,
        longitude=float(updated.longitude) if updated.longitude else None,
        phone=updated.phone,
        email=updated.email,
        logo_url=updated.logo_url,
        is_active=updated.is_active,
        created_at=updated.created_at.isoformat(),
    )
