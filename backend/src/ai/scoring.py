"""Service de scoring IA avancé pour l'attribution intelligente des livreurs.

Modèle multicritère pondéré avec facteurs contextuels :
  - Distance géographique (haversine) — 30%
  - Charge actuelle — 20%
  - Note moyenne historique — 15%
  - Capacité véhicule vs poids — 10%
  - Historique zone de livraison — 10%
  - Fenêtre horaire et ponctualité — 10%
  - Priorité de la commande — 5%
"""

import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.delivery.models import (
    AssignmentStatus,
    CourierProfile,
    DeliveryAssignment,
    DeliveryOrder,
    OrderPriority,
)


MODEL_VERSION = "scoring-v2.0"

WEIGHTS = {
    "distance": 0.30,
    "load": 0.20,
    "rating": 0.15,
    "capacity": 0.10,
    "zone_familiarity": 0.10,
    "punctuality": 0.10,
    "priority_match": 0.05,
}


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    rlat1, rlng1, rlat2, rlng2 = (math.radians(x) for x in (lat1, lng1, lat2, lng2))
    dlat = rlat2 - rlat1
    dlng = rlng2 - rlng1
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def estimate_arrival_min(distance_km: float, vehicle_type: str) -> int:
    speed_map = {
        "bicycle": 12,
        "motorcycle": 30,
        "car": 25,
        "van": 22,
        "truck": 18,
    }
    speed = speed_map.get(vehicle_type, 20)
    return max(3, round((distance_km / speed) * 60))


@dataclass
class ScoringFactors:
    distance_score: float = 0.0
    distance_km: float = 0.0
    load_score: float = 0.0
    active_assignments: int = 0
    rating_score: float = 0.0
    capacity_score: float = 0.0
    weight_ratio: float = 0.0
    zone_familiarity_score: float = 0.0
    deliveries_in_zone: int = 0
    punctuality_score: float = 0.0
    on_time_rate: float = 0.0
    priority_match_score: float = 0.0
    total_score: float = 0.0
    confidence: float = 0.0
    estimated_arrival_min: int = 0


@dataclass
class CourierCandidate:
    courier: CourierProfile
    factors: ScoringFactors = field(default_factory=ScoringFactors)


class AIScoring:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def score_candidates(
        self,
        order: DeliveryOrder,
        couriers: list[CourierProfile],
    ) -> list[CourierCandidate]:
        candidates = []
        for courier in couriers:
            factors = await self._compute_factors(courier, order)
            candidates.append(CourierCandidate(courier=courier, factors=factors))

        candidates.sort(key=lambda c: c.factors.total_score, reverse=True)
        return candidates

    async def _compute_factors(
        self, courier: CourierProfile, order: DeliveryOrder
    ) -> ScoringFactors:
        f = ScoringFactors()

        f.distance_km, f.distance_score = self._calc_distance(courier, order)

        f.active_assignments, f.load_score = self._calc_load(courier)

        f.rating_score = min(1.0, float(courier.rating) / 5.0)

        f.weight_ratio, f.capacity_score = self._calc_capacity(courier, order)

        f.deliveries_in_zone, f.zone_familiarity_score = await self._calc_zone_familiarity(
            courier, order
        )

        f.on_time_rate, f.punctuality_score = await self._calc_punctuality(courier)

        f.priority_match_score = self._calc_priority_match(courier, order)

        f.total_score = (
            f.distance_score * WEIGHTS["distance"]
            + f.load_score * WEIGHTS["load"]
            + f.rating_score * WEIGHTS["rating"]
            + f.capacity_score * WEIGHTS["capacity"]
            + f.zone_familiarity_score * WEIGHTS["zone_familiarity"]
            + f.punctuality_score * WEIGHTS["punctuality"]
            + f.priority_match_score * WEIGHTS["priority_match"]
        )
        f.total_score = round(f.total_score, 4)

        data_points = sum([
            1 if courier.total_deliveries > 0 else 0,
            1 if courier.current_lat is not None else 0,
            1 if f.deliveries_in_zone > 0 else 0,
            1 if f.on_time_rate > 0 else 0,
        ])
        f.confidence = round(min(0.99, 0.50 + data_points * 0.12), 2)

        f.estimated_arrival_min = estimate_arrival_min(
            f.distance_km, courier.vehicle_type.value if courier.vehicle_type else "motorcycle"
        )

        return f

    def _calc_distance(
        self, courier: CourierProfile, order: DeliveryOrder
    ) -> tuple[float, float]:
        if courier.current_lat and courier.current_lng and order.pickup_lat and order.pickup_lng:
            dist = haversine_km(
                float(courier.current_lat), float(courier.current_lng),
                float(order.pickup_lat), float(order.pickup_lng),
            )
            score = max(0, 1.0 - dist / 25.0)
            return round(dist, 2), round(score, 4)
        return 0.0, 0.5

    def _calc_load(self, courier: CourierProfile) -> tuple[int, float]:
        active = len([
            a for a in courier.assignments
            if a.status in (AssignmentStatus.PENDING, AssignmentStatus.ACCEPTED)
        ])
        score = max(0, 1.0 - active * 0.30)
        return active, round(score, 4)

    def _calc_capacity(
        self, courier: CourierProfile, order: DeliveryOrder
    ) -> tuple[float, float]:
        if order.total_weight_kg and courier.max_weight_kg:
            ratio = float(order.total_weight_kg) / float(courier.max_weight_kg)
            if ratio > 1.0:
                return round(ratio, 4), 0.0
            score = 1.0 - ratio * 0.5
            return round(ratio, 4), round(score, 4)
        return 0.0, 0.8

    async def _calc_zone_familiarity(
        self, courier: CourierProfile, order: DeliveryOrder
    ) -> tuple[int, float]:
        if not order.delivery_lat or not order.delivery_lng:
            return 0, 0.5

        lat, lng = float(order.delivery_lat), float(order.delivery_lng)
        radius_deg = 0.02

        stmt = (
            select(func.count())
            .select_from(DeliveryAssignment)
            .join(DeliveryOrder, DeliveryAssignment.order_id == DeliveryOrder.id)
            .where(
                DeliveryAssignment.courier_id == courier.id,
                DeliveryAssignment.status == AssignmentStatus.COMPLETED,
                DeliveryOrder.delivery_lat.between(lat - radius_deg, lat + radius_deg),
                DeliveryOrder.delivery_lng.between(lng - radius_deg, lng + radius_deg),
            )
        )
        result = await self.db.execute(stmt)
        count = result.scalar() or 0

        score = min(1.0, count / 10.0)
        return count, round(score, 4)

    async def _calc_punctuality(self, courier: CourierProfile) -> tuple[float, float]:
        if courier.total_deliveries < 3:
            return 0.0, 0.7

        stmt = (
            select(
                func.count().label("total"),
                func.count()
                .filter(DeliveryAssignment.delivered_at <= DeliveryAssignment.expires_at)
                .label("on_time"),
            )
            .where(
                DeliveryAssignment.courier_id == courier.id,
                DeliveryAssignment.status == AssignmentStatus.COMPLETED,
            )
        )
        result = await self.db.execute(stmt)
        row = result.one_or_none()
        if not row or row.total == 0:
            return 0.0, 0.7

        rate = row.on_time / row.total
        return round(rate, 4), round(rate, 4)

    def _calc_priority_match(
        self, courier: CourierProfile, order: DeliveryOrder
    ) -> float:
        if order.priority == OrderPriority.URGENT:
            speed_rank = {"motorcycle": 1.0, "bicycle": 0.7, "car": 0.8, "van": 0.6, "truck": 0.4}
        elif order.priority == OrderPriority.HIGH:
            speed_rank = {"motorcycle": 0.9, "car": 0.9, "bicycle": 0.6, "van": 0.7, "truck": 0.5}
        else:
            return 0.8
        vtype = courier.vehicle_type.value if courier.vehicle_type else "motorcycle"
        return speed_rank.get(vtype, 0.6)

    def factors_to_dict(self, f: ScoringFactors) -> dict:
        return {
            "distance_km": f.distance_km,
            "distance_score": f.distance_score,
            "load_score": f.load_score,
            "active_assignments": f.active_assignments,
            "rating_score": f.rating_score,
            "capacity_score": f.capacity_score,
            "weight_ratio": f.weight_ratio,
            "zone_familiarity_score": f.zone_familiarity_score,
            "deliveries_in_zone": f.deliveries_in_zone,
            "punctuality_score": f.punctuality_score,
            "on_time_rate": f.on_time_rate,
            "priority_match_score": f.priority_match_score,
            "total_score": f.total_score,
            "confidence": f.confidence,
            "estimated_arrival_min": f.estimated_arrival_min,
            "model_version": MODEL_VERSION,
            "weights": WEIGHTS,
        }
