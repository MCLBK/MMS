import uuid
from pydantic import BaseModel, Field


class ScoringRequest(BaseModel):
    order_id: uuid.UUID


class ScoringResult(BaseModel):
    courier_id: uuid.UUID
    courier_name: str
    score: float
    confidence: float
    estimated_arrival_min: int
    distance_km: float
    factors: dict


class ScoringResponse(BaseModel):
    order_id: uuid.UUID
    candidates: list[ScoringResult]
    model_version: str


class PredictionTimeRequest(BaseModel):
    pickup_lat: float | None = None
    pickup_lng: float | None = None
    delivery_lat: float | None = None
    delivery_lng: float | None = None
    priority: str = "normal"
    weight_kg: float | None = None


class PredictionTimeResponse(BaseModel):
    estimated_minutes: int
    confidence: float
    factors: dict


class VolumeForecastItem(BaseModel):
    date: str
    predicted_orders: int
    confidence: float
    trend: str


class HotZoneResponse(BaseModel):
    center_lat: float
    center_lng: float
    radius_km: float
    order_count: int
    avg_delivery_time_min: float | None
    demand_level: str


class RiskRequest(BaseModel):
    order_id: uuid.UUID


class RiskResponse(BaseModel):
    risk_score: float
    risk_level: str
    factors: list[str]
    recommendations: list[str]


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_history: list[dict] | None = None


class ChatResponse(BaseModel):
    message: str
    context: dict
    source: str
    suggestions: list[str]
