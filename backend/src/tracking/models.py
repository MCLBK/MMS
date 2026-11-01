import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Numeric, SmallInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class GPSLocation(Base):
    __tablename__ = "gps_locations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    courier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courier_profiles.id", ondelete="CASCADE"), nullable=False
    )
    assignment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("delivery_assignments.id"), nullable=True
    )
    latitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)
    accuracy_m: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    speed_kmh: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    heading: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    battery_level: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    courier: Mapped["CourierProfile"] = relationship(back_populates="gps_locations")

    __table_args__ = (
        Index("ix_gps_locations_courier_recorded", "courier_id", "recorded_at"),
        Index("ix_gps_locations_assignment", "assignment_id"),
    )


from src.delivery.models import CourierProfile  # noqa: E402
