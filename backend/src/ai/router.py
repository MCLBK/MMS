import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.assistant import AIAssistant
from src.ai.predictions import PredictionService
from src.ai.schemas import (
    ChatRequest,
    ChatResponse,
    HotZoneResponse,
    PredictionTimeRequest,
    PredictionTimeResponse,
    RiskRequest,
    RiskResponse,
    ScoringRequest,
    ScoringResponse,
    ScoringResult,
    VolumeForecastItem,
)
from src.ai.scoring import MODEL_VERSION, AIScoring
from src.couriers.repository import CourierRepository
from src.database.base import get_db
from src.delivery.repository import DeliveryRepository
from src.middlewares.tenant import resolve_tenant

router = APIRouter(tags=["AI"])


@router.post(
    "/companies/{company_id}/ai/scoring",
    response_model=ScoringResponse,
)
async def score_couriers_for_order(
    company_id: uuid.UUID,
    body: ScoringRequest,
    db: AsyncSession = Depends(get_db),
    _tenant=Depends(resolve_tenant),
):
    delivery_repo = DeliveryRepository(db)
    courier_repo = CourierRepository(db)

    order = await delivery_repo.get_order_by_id(body.order_id, company_id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable")

    available = await courier_repo.get_available_couriers(company_id)
    if not available:
        raise HTTPException(status_code=404, detail="Aucun livreur disponible")

    scoring = AIScoring(db)
    candidates = await scoring.score_candidates(order, available)

    results = []
    for c in candidates:
        name = c.courier.user.full_name if c.courier.user else "Livreur"
        results.append(
            ScoringResult(
                courier_id=c.courier.id,
                courier_name=name,
                score=c.factors.total_score,
                confidence=c.factors.confidence,
                estimated_arrival_min=c.factors.estimated_arrival_min,
                distance_km=c.factors.distance_km,
                factors=scoring.factors_to_dict(c.factors),
            )
        )

    return ScoringResponse(
        order_id=body.order_id,
        candidates=results,
        model_version=MODEL_VERSION,
    )


@router.post(
    "/companies/{company_id}/ai/predict-time",
    response_model=PredictionTimeResponse,
)
async def predict_delivery_time(
    company_id: uuid.UUID,
    body: PredictionTimeRequest,
    db: AsyncSession = Depends(get_db),
    _tenant=Depends(resolve_tenant),
):
    svc = PredictionService(db)
    pred = await svc.predict_delivery_time(
        company_id,
        body.pickup_lat,
        body.pickup_lng,
        body.delivery_lat,
        body.delivery_lng,
        body.priority,
        body.weight_kg,
    )
    return PredictionTimeResponse(
        estimated_minutes=pred.estimated_minutes,
        confidence=pred.confidence,
        factors=pred.factors,
    )


@router.get(
    "/companies/{company_id}/ai/forecast",
    response_model=list[VolumeForecastItem],
)
async def forecast_order_volume(
    company_id: uuid.UUID,
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    _tenant=Depends(resolve_tenant),
):
    svc = PredictionService(db)
    forecasts = await svc.forecast_volume(company_id, min(days, 30))
    return [
        VolumeForecastItem(
            date=f.date,
            predicted_orders=f.predicted_orders,
            confidence=f.confidence,
            trend=f.trend,
        )
        for f in forecasts
    ]


@router.get(
    "/companies/{company_id}/ai/hot-zones",
    response_model=list[HotZoneResponse],
)
async def get_hot_zones(
    company_id: uuid.UUID,
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    _tenant=Depends(resolve_tenant),
):
    svc = PredictionService(db)
    zones = await svc.detect_hot_zones(company_id, min(days, 60))
    return [
        HotZoneResponse(
            center_lat=z.center_lat,
            center_lng=z.center_lng,
            radius_km=z.radius_km,
            order_count=z.order_count,
            avg_delivery_time_min=z.avg_delivery_time_min,
            demand_level=z.demand_level,
        )
        for z in zones
    ]


@router.post(
    "/companies/{company_id}/ai/risk",
    response_model=RiskResponse,
)
async def assess_order_risk(
    company_id: uuid.UUID,
    body: RiskRequest,
    db: AsyncSession = Depends(get_db),
    _tenant=Depends(resolve_tenant),
):
    delivery_repo = DeliveryRepository(db)
    order = await delivery_repo.get_order_by_id(body.order_id, company_id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable")

    svc = PredictionService(db)
    risk = await svc.assess_delivery_risk(company_id, order)
    return RiskResponse(
        risk_score=risk.risk_score,
        risk_level=risk.risk_level,
        factors=risk.factors,
        recommendations=risk.recommendations,
    )


@router.post(
    "/companies/{company_id}/ai/chat",
    response_model=ChatResponse,
)
async def ai_chat(
    company_id: uuid.UUID,
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
    _tenant=Depends(resolve_tenant),
):
    assistant = AIAssistant(db)
    resp = await assistant.chat(company_id, body.message, body.conversation_history)
    return ChatResponse(
        message=resp.message,
        context=resp.context,
        source=resp.source,
        suggestions=resp.suggestions,
    )
