import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base, UUIDMixin


class AIRecommendation(Base, UUIDMixin):
    __tablename__ = "ai_recommendations"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("delivery_orders.id", ondelete="CASCADE"), nullable=False
    )
    courier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courier_profiles.id"), nullable=False
    )
    score: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    factors: Mapped[dict] = mapped_column(JSON, nullable=False)
    distance_km: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    estimated_arrival_min: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    order: Mapped["DeliveryOrder"] = relationship(back_populates="ai_recommendations")


from src.delivery.models import DeliveryOrder  # noqa: E402
