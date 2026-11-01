import uuid

from sqlalchemy import Boolean, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base, TimestampMixin, UUIDMixin


class Company(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    address: Mapped[str] = mapped_column(Text, default="")
    city: Mapped[str] = mapped_column(String(100), default="")
    country: Mapped[str] = mapped_column(String(100), default="")
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    settings: Mapped[dict | None] = mapped_column(JSON, default=dict)

    memberships: Mapped[list["CompanyMembership"]] = relationship(back_populates="company")
    courier_profiles: Mapped[list["CourierProfile"]] = relationship(back_populates="company")
    customers: Mapped[list["Customer"]] = relationship(back_populates="company")
    delivery_orders: Mapped[list["DeliveryOrder"]] = relationship(back_populates="company")


from src.users.models import CompanyMembership  # noqa: E402
from src.delivery.models import CourierProfile, Customer, DeliveryOrder  # noqa: E402
