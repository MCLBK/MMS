import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class GPSLocationCreate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy_m: float | None = None
    speed_kmh: float | None = None
    heading: float | None = None
    battery_level: int | None = Field(None, ge=0, le=100)
    assignment_id: uuid.UUID | None = None


class GPSLocationResponse(BaseModel):
    id: int
    courier_id: uuid.UUID
    latitude: float
    longitude: float
    accuracy_m: float | None
    speed_kmh: float | None
    heading: float | None
    battery_level: int | None
    recorded_at: str

    model_config = {"from_attributes": True}


class CourierPosition(BaseModel):
    courier_id: uuid.UUID
    courier_name: str
    latitude: float
    longitude: float
    speed_kmh: float | None
    battery_level: int | None
    recorded_at: str
    status: str
