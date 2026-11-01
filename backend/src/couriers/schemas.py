import uuid

from pydantic import BaseModel, Field

from src.delivery.models import CourierStatus, VehicleType


class CourierProfileCreate(BaseModel):
    user_id: uuid.UUID
    vehicle_type: VehicleType = VehicleType.MOTORCYCLE
    max_weight_kg: float = 20.0
    max_volume_m3: float = 0.5
    license_number: str | None = None


class CourierProfileUpdate(BaseModel):
    vehicle_type: VehicleType | None = None
    max_weight_kg: float | None = None
    max_volume_m3: float | None = None
    license_number: str | None = None
    status: CourierStatus | None = None
    is_active: bool | None = None


class CourierPositionUpdate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class CourierListItem(BaseModel):
    id: uuid.UUID
    user_name: str
    vehicle_type: VehicleType
    status: CourierStatus
    rating: float
    total_deliveries: int
    is_active: bool

    model_config = {"from_attributes": True}


class CourierDetail(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    user_name: str
    user_email: str
    vehicle_type: VehicleType
    max_weight_kg: float
    max_volume_m3: float
    license_number: str | None
    status: CourierStatus
    current_lat: float | None
    current_lng: float | None
    last_position_at: str | None
    rating: float
    total_deliveries: int
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}
