import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.delivery.models import OrderPriority, OrderStatus

# ─── Items ───────────────────────────────────────────────────


class DeliveryItemCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=300)
    quantity: int = Field(1, ge=1)
    weight_kg: float | None = None
    is_fragile: bool = False
    requires_signature: bool = False


class DeliveryItemResponse(BaseModel):
    id: uuid.UUID
    description: str
    quantity: int
    weight_kg: float | None
    is_fragile: bool
    requires_signature: bool

    model_config = {"from_attributes": True}


# ─── Customer (inline) ───────────────────────────────────────


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(..., min_length=5, max_length=20)
    email: str | None = None
    address: str = ""
    city: str = ""
    latitude: float | None = None
    longitude: float | None = None
    notes: str | None = None


class CustomerResponse(BaseModel):
    id: uuid.UUID
    name: str
    phone: str
    email: str | None
    address: str
    city: str

    model_config = {"from_attributes": True}


# ─── Orders ──────────────────────────────────────────────────


class OrderCreate(BaseModel):
    customer_id: uuid.UUID | None = None
    new_customer: CustomerCreate | None = None
    priority: OrderPriority = OrderPriority.NORMAL
    pickup_address: str = Field(..., min_length=3)
    pickup_lat: float | None = None
    pickup_lng: float | None = None
    delivery_address: str = Field(..., min_length=3)
    delivery_lat: float | None = None
    delivery_lng: float | None = None
    requested_delivery_at: datetime | None = None
    special_instructions: str | None = None
    items: list[DeliveryItemCreate] = Field(default_factory=list)


class OrderUpdate(BaseModel):
    priority: OrderPriority | None = None
    pickup_address: str | None = None
    pickup_lat: float | None = None
    pickup_lng: float | None = None
    delivery_address: str | None = None
    delivery_lat: float | None = None
    delivery_lng: float | None = None
    requested_delivery_at: datetime | None = None
    special_instructions: str | None = None


class StatusTransition(BaseModel):
    new_status: OrderStatus
    reason: str | None = None


class OrderListItem(BaseModel):
    id: uuid.UUID
    reference: str
    status: OrderStatus
    priority: OrderPriority
    customer_name: str
    pickup_address: str
    delivery_address: str
    created_at: str

    model_config = {"from_attributes": True}


class OrderDetail(BaseModel):
    id: uuid.UUID
    reference: str
    status: OrderStatus
    priority: OrderPriority
    pickup_address: str
    pickup_lat: float | None
    pickup_lng: float | None
    delivery_address: str
    delivery_lat: float | None
    delivery_lng: float | None
    total_weight_kg: float | None
    estimated_distance_km: float | None
    estimated_duration_min: int | None
    requested_delivery_at: str | None
    special_instructions: str | None
    customer: CustomerResponse
    items: list[DeliveryItemResponse]
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class PaginatedOrders(BaseModel):
    items: list[OrderListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
