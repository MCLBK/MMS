"""Service de prédictions IA pour l'aide à la décision.

Fonctionnalités :
  - Estimation du délai de livraison
  - Prédiction du volume de commandes (série temporelle simple)
  - Détection de zones à forte demande (hot zones)
  - Score de risque d'échec de livraison
"""

import math
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import case, cast, Date, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.delivery.models import (
    AssignmentStatus,
    CourierProfile,
    DeliveryAssignment,
    DeliveryOrder,
    OrderPriority,
    OrderStatus,
)


@dataclass
class DeliveryTimePrediction:
    estimated_minutes: int
    confidence: float
    factors: dict


@dataclass
class VolumeForecast:
    date: str
    predicted_orders: int
    confidence: float
    trend: str


@dataclass
class HotZone:
    center_lat: float
    center_lng: float
    radius_km: float
    order_count: int
    avg_delivery_time_min: float | None
    demand_level: str


@dataclass
class RiskAssessment:
    risk_score: float
    risk_level: str
    factors: list[str]
    recommendations: list[str]


class PredictionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def predict_delivery_time(
        self,
        company_id: uuid.UUID,
        pickup_lat: float | None,
        pickup_lng: float | None,
        delivery_lat: float | None,
        delivery_lng: float | None,
        priority: str = "normal",
        weight_kg: float | None = None,
    ) -> DeliveryTimePrediction:
        base_minutes = 30

        if pickup_lat and pickup_lng and delivery_lat and delivery_lng:
            from src.ai.scoring import haversine_km
            distance = haversine_km(pickup_lat, pickup_lng, delivery_lat, delivery_lng)
            distance_minutes = distance * 3.0
        else:
            distance = 0.0
            distance_minutes = 15.0

        now = datetime.now(timezone.utc)
        hour = now.hour
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            traffic_factor = 1.4
        elif 12 <= hour <= 14:
            traffic_factor = 1.2
        else:
            traffic_factor = 1.0

        priority_factor = {"urgent": 0.8, "high": 0.9, "normal": 1.0, "low": 1.1}.get(
            priority, 1.0
        )

        weight_factor = 1.0
        if weight_kg and weight_kg > 30:
            weight_factor = 1.15
        elif weight_kg and weight_kg > 50:
            weight_factor = 1.30

        historical_avg = await self._get_historical_avg_time(company_id)
        if historical_avg:
            base_minutes = (base_minutes + historical_avg) / 2

        estimated = (base_minutes + distance_minutes) * traffic_factor * priority_factor * weight_factor
        estimated = max(10, round(estimated))

        data_points = sum([1 if distance > 0 else 0, 1 if historical_avg else 0, 1])
        confidence = min(0.95, 0.40 + data_points * 0.18)

        return DeliveryTimePrediction(
            estimated_minutes=estimated,
            confidence=round(confidence, 2),
            factors={
                "distance_km": round(distance, 2),
                "distance_minutes": round(distance_minutes, 1),
                "traffic_factor": traffic_factor,
                "priority_factor": priority_factor,
                "weight_factor": weight_factor,
                "historical_avg_min": round(historical_avg, 1) if historical_avg else None,
                "hour": hour,
            },
        )

    async def forecast_volume(
        self, company_id: uuid.UUID, days_ahead: int = 7
    ) -> list[VolumeForecast]:
        stmt = (
            select(
                cast(DeliveryOrder.created_at, Date).label("day"),
                func.count().label("cnt"),
            )
            .where(
                DeliveryOrder.company_id == company_id,
                DeliveryOrder.created_at >= datetime.now(timezone.utc) - timedelta(days=30),
            )
            .group_by("day")
            .order_by("day")
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        if not rows:
            return [
                VolumeForecast(
                    date=(datetime.now(timezone.utc) + timedelta(days=i)).strftime("%Y-%m-%d"),
                    predicted_orders=0,
                    confidence=0.3,
                    trend="stable",
                )
                for i in range(1, days_ahead + 1)
            ]

        daily_counts = [r.cnt for r in rows]
        avg = sum(daily_counts) / len(daily_counts)

        if len(daily_counts) >= 7:
            recent_avg = sum(daily_counts[-7:]) / 7
            trend_factor = recent_avg / avg if avg > 0 else 1.0
        else:
            trend_factor = 1.0

        trend_label = "up" if trend_factor > 1.1 else "down" if trend_factor < 0.9 else "stable"

        dow_counts: dict[int, list[int]] = {}
        for r in rows:
            dow = r.day.weekday()
            dow_counts.setdefault(dow, []).append(r.cnt)
        dow_avg = {dow: sum(v) / len(v) for dow, v in dow_counts.items()}

        forecasts = []
        for i in range(1, days_ahead + 1):
            target_date = datetime.now(timezone.utc) + timedelta(days=i)
            dow = target_date.weekday()
            base = dow_avg.get(dow, avg)
            predicted = max(0, round(base * trend_factor))
            conf = min(0.90, 0.50 + len(daily_counts) * 0.01) - i * 0.03
            forecasts.append(
                VolumeForecast(
                    date=target_date.strftime("%Y-%m-%d"),
                    predicted_orders=predicted,
                    confidence=round(max(0.20, conf), 2),
                    trend=trend_label,
                )
            )

        return forecasts

    async def detect_hot_zones(
        self, company_id: uuid.UUID, days: int = 7, grid_size: float = 0.02
    ) -> list[HotZone]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = (
            select(
                DeliveryOrder.delivery_lat,
                DeliveryOrder.delivery_lng,
            )
            .where(
                DeliveryOrder.company_id == company_id,
                DeliveryOrder.created_at >= since,
                DeliveryOrder.delivery_lat.isnot(None),
                DeliveryOrder.delivery_lng.isnot(None),
            )
        )
        result = await self.db.execute(stmt)
        points = [(float(r.delivery_lat), float(r.delivery_lng)) for r in result.all()]

        if not points:
            return []

        grid: dict[tuple[int, int], list[tuple[float, float]]] = {}
        for lat, lng in points:
            key = (round(lat / grid_size), round(lng / grid_size))
            grid.setdefault(key, []).append((lat, lng))

        zones = []
        for cell_key, cell_points in grid.items():
            if len(cell_points) < 3:
                continue
            avg_lat = sum(p[0] for p in cell_points) / len(cell_points)
            avg_lng = sum(p[1] for p in cell_points) / len(cell_points)
            count = len(cell_points)
            demand = "high" if count >= 15 else "medium" if count >= 7 else "low"
            zones.append(
                HotZone(
                    center_lat=round(avg_lat, 6),
                    center_lng=round(avg_lng, 6),
                    radius_km=round(grid_size * 111, 1),
                    order_count=count,
                    avg_delivery_time_min=None,
                    demand_level=demand,
                )
            )

        zones.sort(key=lambda z: z.order_count, reverse=True)
        return zones[:20]

    async def assess_delivery_risk(
        self,
        company_id: uuid.UUID,
        order: DeliveryOrder,
    ) -> RiskAssessment:
        risk = 0.0
        factors = []
        recommendations = []

        if order.priority == OrderPriority.URGENT:
            risk += 0.15
            factors.append("Priorité urgente augmente le risque de retard")
        elif order.priority == OrderPriority.HIGH:
            risk += 0.08
            factors.append("Priorité haute modérément risquée")

        if order.total_weight_kg and float(order.total_weight_kg) > 40:
            risk += 0.12
            factors.append(f"Poids élevé ({order.total_weight_kg} kg)")
            recommendations.append("Privilégier un véhicule utilitaire")

        has_fragile = any(item.is_fragile for item in order.items)
        if has_fragile:
            risk += 0.10
            factors.append("Contient des articles fragiles")
            recommendations.append("Sélectionner un livreur avec note >= 4.5")

        now = datetime.now(timezone.utc)
        if now.hour >= 18 or now.hour < 6:
            risk += 0.10
            factors.append("Livraison en horaire tardif/nocturne")

        if order.pickup_lat and order.pickup_lng and order.delivery_lat and order.delivery_lng:
            from src.ai.scoring import haversine_km
            dist = haversine_km(
                float(order.pickup_lat), float(order.pickup_lng),
                float(order.delivery_lat), float(order.delivery_lng),
            )
            if dist > 15:
                risk += 0.12
                factors.append(f"Longue distance ({dist:.1f} km)")
                recommendations.append("Prévoir un délai supplémentaire")

        fail_rate = await self._get_zone_failure_rate(company_id, order)
        if fail_rate and fail_rate > 0.15:
            risk += 0.15
            factors.append(f"Zone avec taux d'échec élevé ({fail_rate:.0%})")
            recommendations.append("Contacter le client pour confirmer l'adresse")

        risk = min(1.0, risk)
        level = "critical" if risk >= 0.6 else "high" if risk >= 0.4 else "medium" if risk >= 0.2 else "low"

        if not recommendations:
            recommendations.append("Aucune action spéciale requise")

        return RiskAssessment(
            risk_score=round(risk, 2),
            risk_level=level,
            factors=factors,
            recommendations=recommendations,
        )

    async def _get_historical_avg_time(self, company_id: uuid.UUID) -> float | None:
        stmt = (
            select(
                func.avg(
                    func.extract("epoch", DeliveryAssignment.delivered_at - DeliveryAssignment.assigned_at) / 60
                )
            )
            .join(DeliveryOrder, DeliveryAssignment.order_id == DeliveryOrder.id)
            .where(
                DeliveryOrder.company_id == company_id,
                DeliveryAssignment.status == AssignmentStatus.COMPLETED,
                DeliveryAssignment.delivered_at.isnot(None),
            )
        )
        result = await self.db.execute(stmt)
        avg = result.scalar()
        return float(avg) if avg else None

    async def _get_zone_failure_rate(
        self, company_id: uuid.UUID, order: DeliveryOrder
    ) -> float | None:
        if not order.delivery_lat or not order.delivery_lng:
            return None
        lat, lng = float(order.delivery_lat), float(order.delivery_lng)
        radius = 0.02
        stmt = (
            select(
                func.count().label("total"),
                func.count().filter(
                    DeliveryOrder.status.in_([
                        OrderStatus.DELIVERY_FAILED,
                        OrderStatus.CANCELLED,
                    ])
                ).label("failed"),
            )
            .where(
                DeliveryOrder.company_id == company_id,
                DeliveryOrder.delivery_lat.between(lat - radius, lat + radius),
                DeliveryOrder.delivery_lng.between(lng - radius, lng + radius),
            )
        )
        result = await self.db.execute(stmt)
        row = result.one_or_none()
        if not row or row.total < 5:
            return None
        return row.failed / row.total
