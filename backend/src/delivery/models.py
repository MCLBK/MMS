import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base, TimestampMixin, UUIDMixin

# ─── Enums ────────────────────────────────────────────────────


class VehicleType(enum.StrEnum):
    BICYCLE = "bicycle"
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    VAN = "van"
    TRUCK = "truck"


class CourierStatus(enum.StrEnum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"


class OrderStatus(enum.StrEnum):
    DRAFT = "draft"
    PENDING = "pending"
    ANALYZING = "analyzing"
    READY_TO_ASSIGN = "ready_to_assign"
    ASSIGNING = "assigning"
    ASSIGNED = "assigned"
    COURIER_ACCEPTED = "courier_accepted"
    PICKUP_IN_PROGRESS = "pickup_in_progress"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    ARRIVING = "arriving"
    DELIVERED = "delivered"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    COURIER_REFUSED = "courier_refused"
    EXPIRED = "expired"
    DELIVERY_FAILED = "delivery_failed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"


class OrderPriority(enum.StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class AssignmentStatus(enum.StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REFUSED = "refused"
    EXPIRED = "expired"
    COMPLETED = "completed"
    FAILED = "failed"


class ProofType(enum.StrEnum):
    PHOTO = "photo"
    SIGNATURE = "signature"
    CODE = "code"


class ConfirmationSource(enum.StrEnum):
    COURIER = "courier"
    CUSTOMER = "customer"
    SYSTEM = "system"


class ConfirmationStatus(enum.StrEnum):
    CONFIRMED = "confirmed"
    DISPUTED = "disputed"
    PARTIAL = "partial"


# ─── Models ───────────────────────────────────────────────────


class CourierProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "courier_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vehicle_type: Mapped[VehicleType] = mapped_column(
        Enum(VehicleType, name="vehicle_type"), default=VehicleType.MOTORCYCLE
    )
    max_weight_kg: Mapped[float] = mapped_column(Numeric(8, 2), default=20.0)
    max_volume_m3: Mapped[float] = mapped_column(Numeric(8, 3), default=0.5)
    license_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[CourierStatus] = mapped_column(
        Enum(CourierStatus, name="courier_status"), default=CourierStatus.OFFLINE
    )
    current_lat: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    current_lng: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    last_position_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    rating: Mapped[float] = mapped_column(Numeric(3, 2), default=5.0)
    total_deliveries: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship(lazy="selectin")
    company: Mapped["Company"] = relationship(back_populates="courier_profiles")
    assignments: Mapped[list["DeliveryAssignment"]] = relationship(back_populates="courier")
    gps_locations: Mapped[list["GPSLocation"]] = relationship(back_populates="courier")


class Customer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "customers"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str] = mapped_column(Text, default="")
    city: Mapped[str] = mapped_column(String(100), default="")
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    company: Mapped["Company"] = relationship(back_populates="customers")
    delivery_orders: Mapped[list["DeliveryOrder"]] = relationship(back_populates="customer")


class DeliveryOrder(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "delivery_orders"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    reference: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status"), default=OrderStatus.DRAFT, index=True
    )
    priority: Mapped[OrderPriority] = mapped_column(
        Enum(OrderPriority, name="order_priority"), default=OrderPriority.NORMAL
    )

    pickup_address: Mapped[str] = mapped_column(Text, nullable=False)
    pickup_lat: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    pickup_lng: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    delivery_address: Mapped[str] = mapped_column(Text, nullable=False)
    delivery_lat: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    delivery_lng: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)

    total_weight_kg: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    total_volume_m3: Mapped[float | None] = mapped_column(Numeric(8, 3), nullable=True)
    estimated_distance_km: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    estimated_duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    requested_delivery_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    special_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    company: Mapped["Company"] = relationship(back_populates="delivery_orders")
    customer: Mapped["Customer"] = relationship(back_populates="delivery_orders")
    items: Mapped[list["DeliveryItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    assignments: Mapped[list["DeliveryAssignment"]] = relationship(back_populates="order")
    status_history: Mapped[list["DeliveryStatusHistory"]] = relationship(
        back_populates="order", order_by="DeliveryStatusHistory.created_at"
    )
    ai_recommendations: Mapped[list["AIRecommendation"]] = relationship(back_populates="order")


class DeliveryItem(Base, UUIDMixin):
    __tablename__ = "delivery_items"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("delivery_orders.id", ondelete="CASCADE"), nullable=False
    )
    description: Mapped[str] = mapped_column(String(300), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    weight_kg: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    is_fragile: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_signature: Mapped[bool] = mapped_column(Boolean, default=False)

    order: Mapped["DeliveryOrder"] = relationship(back_populates="items")


class DeliveryAssignment(Base, UUIDMixin):
    __tablename__ = "delivery_assignments"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("delivery_orders.id", ondelete="CASCADE"), nullable=False
    )
    courier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courier_profiles.id"), nullable=False, index=True
    )
    status: Mapped[AssignmentStatus] = mapped_column(
        Enum(AssignmentStatus, name="assignment_status"),
        default=AssignmentStatus.PENDING,
        index=True,
    )
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    pickup_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ai_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    ai_reasoning: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    order: Mapped["DeliveryOrder"] = relationship(back_populates="assignments")
    courier: Mapped["CourierProfile"] = relationship(back_populates="assignments")
    proofs: Mapped[list["DeliveryProof"]] = relationship(back_populates="assignment")
    confirmations: Mapped[list["DeliveryConfirmation"]] = relationship(back_populates="assignment")


class DeliveryStatusHistory(Base, UUIDMixin):
    __tablename__ = "delivery_status_history"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("delivery_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    changed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    old_status: Mapped[str] = mapped_column(String(50), nullable=False)
    new_status: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    order: Mapped["DeliveryOrder"] = relationship(back_populates="status_history")


class DeliveryProof(Base, UUIDMixin):
    __tablename__ = "delivery_proofs"

    assignment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("delivery_assignments.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[ProofType] = mapped_column(Enum(ProofType, name="proof_type"), nullable=False)
    file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    verification_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    assignment: Mapped["DeliveryAssignment"] = relationship(back_populates="proofs")


class DeliveryConfirmation(Base, UUIDMixin):
    __tablename__ = "delivery_confirmations"

    assignment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("delivery_assignments.id", ondelete="CASCADE"),
        nullable=False,
    )
    confirmed_by: Mapped[ConfirmationSource] = mapped_column(
        Enum(ConfirmationSource, name="confirmation_source"), nullable=False
    )
    status: Mapped[ConfirmationStatus] = mapped_column(
        Enum(ConfirmationStatus, name="confirmation_status"), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    confirmed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    assignment: Mapped["DeliveryAssignment"] = relationship(back_populates="confirmations")


# Forward imports
from src.ai.models import AIRecommendation  # noqa: E402
from src.companies.models import Company  # noqa: E402
from src.tracking.models import GPSLocation  # noqa: E402
from src.users.models import User  # noqa: E402
