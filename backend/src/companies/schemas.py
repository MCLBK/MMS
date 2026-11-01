import uuid

from pydantic import BaseModel, Field

from src.schemas.common import BaseSchema


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9\-]+$")
    address: str = ""
    city: str = ""
    country: str = ""
    latitude: float | None = None
    longitude: float | None = None
    phone: str | None = None
    email: str | None = None


class CompanyUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    phone: str | None = None
    email: str | None = None
    is_active: bool | None = None


class CompanyListItem(BaseSchema):
    id: uuid.UUID
    name: str
    slug: str
    city: str
    country: str
    is_active: bool


class CompanyDetail(CompanyListItem):
    address: str
    latitude: float | None
    longitude: float | None
    phone: str | None
    email: str | None
    logo_url: str | None
    created_at: str
