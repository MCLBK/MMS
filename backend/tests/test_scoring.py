"""Tests unitaires pour le service de scoring IA."""

import math
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from src.ai.scoring import (
    haversine_km,
    estimate_arrival_min,
    AIScoring,
    ScoringFactors,
    WEIGHTS,
    MODEL_VERSION,
)


class TestHaversine:
    def test_same_point_returns_zero(self):
        assert haversine_km(0.0, 0.0, 0.0, 0.0) == 0.0

    def test_known_distance(self):
        # Paris (48.8566, 2.3522) -> Lyon (45.7640, 4.8357) ≈ 392 km
        dist = haversine_km(48.8566, 2.3522, 45.7640, 4.8357)
        assert 385 < dist < 400

    def test_short_distance(self):
        # ~1.1 km between two nearby points
        dist = haversine_km(5.3484, -4.0167, 5.3584, -4.0167)
        assert 1.0 < dist < 1.2

    def test_symmetry(self):
        d1 = haversine_km(5.0, -4.0, 6.0, -3.0)
        d2 = haversine_km(6.0, -3.0, 5.0, -4.0)
        assert abs(d1 - d2) < 0.001


class TestEstimateArrival:
    def test_motorcycle_speed(self):
        minutes = estimate_arrival_min(30.0, "motorcycle")
        assert minutes == 60  # 30km / 30km/h = 1h

    def test_bicycle_slower(self):
        bike = estimate_arrival_min(10.0, "bicycle")
        moto = estimate_arrival_min(10.0, "motorcycle")
        assert bike > moto

    def test_minimum_3_minutes(self):
        assert estimate_arrival_min(0.1, "motorcycle") >= 3

    def test_unknown_vehicle_uses_default(self):
        minutes = estimate_arrival_min(20.0, "hoverboard")
        assert minutes == 60  # 20km / 20km/h = 1h


class TestScoringWeights:
    def test_weights_sum_to_one(self):
        total = sum(WEIGHTS.values())
        assert abs(total - 1.0) < 0.001

    def test_model_version_format(self):
        assert MODEL_VERSION.startswith("scoring-v")


class TestScoringFactors:
    def test_default_values(self):
        f = ScoringFactors()
        assert f.total_score == 0.0
        assert f.confidence == 0.0
        assert f.distance_km == 0.0

    def test_factors_to_dict(self):
        scoring = AIScoring.__new__(AIScoring)
        f = ScoringFactors(total_score=0.85, confidence=0.74, distance_km=3.5)
        d = scoring.factors_to_dict(f)
        assert d["total_score"] == 0.85
        assert d["confidence"] == 0.74
        assert d["model_version"] == MODEL_VERSION
        assert "weights" in d


class TestScoringCalcDistance:
    def test_no_coordinates_returns_default(self):
        scoring = AIScoring.__new__(AIScoring)
        courier = MagicMock()
        courier.current_lat = None
        courier.current_lng = None
        order = MagicMock()
        order.pickup_lat = None
        order.pickup_lng = None

        dist, score = scoring._calc_distance(courier, order)
        assert dist == 0.0
        assert score == 0.5

    def test_close_distance_high_score(self):
        scoring = AIScoring.__new__(AIScoring)
        courier = MagicMock()
        courier.current_lat = 5.3484
        courier.current_lng = -4.0167
        order = MagicMock()
        order.pickup_lat = 5.3500
        order.pickup_lng = -4.0150

        dist, score = scoring._calc_distance(courier, order)
        assert dist < 1.0
        assert score > 0.9

    def test_far_distance_low_score(self):
        scoring = AIScoring.__new__(AIScoring)
        courier = MagicMock()
        courier.current_lat = 5.3484
        courier.current_lng = -4.0167
        order = MagicMock()
        order.pickup_lat = 5.6000
        order.pickup_lng = -3.8000

        dist, score = scoring._calc_distance(courier, order)
        assert dist > 20
        assert score <= 0.2


class TestScoringCalcLoad:
    def test_no_assignments(self):
        scoring = AIScoring.__new__(AIScoring)
        courier = MagicMock()
        courier.assignments = []

        active, score = scoring._calc_load(courier)
        assert active == 0
        assert score == 1.0

    def test_high_load_low_score(self):
        from src.delivery.models import AssignmentStatus
        scoring = AIScoring.__new__(AIScoring)
        courier = MagicMock()
        a1 = MagicMock()
        a1.status = AssignmentStatus.PENDING
        a2 = MagicMock()
        a2.status = AssignmentStatus.ACCEPTED
        a3 = MagicMock()
        a3.status = AssignmentStatus.COMPLETED  # not counted
        courier.assignments = [a1, a2, a3]

        active, score = scoring._calc_load(courier)
        assert active == 2
        assert score < 0.5


class TestScoringCalcCapacity:
    def test_no_weight_data(self):
        scoring = AIScoring.__new__(AIScoring)
        courier = MagicMock()
        courier.max_weight_kg = None
        order = MagicMock()
        order.total_weight_kg = None

        ratio, score = scoring._calc_capacity(courier, order)
        assert score == 0.8

    def test_overweight_zero_score(self):
        scoring = AIScoring.__new__(AIScoring)
        courier = MagicMock()
        courier.max_weight_kg = 10.0
        order = MagicMock()
        order.total_weight_kg = 15.0

        ratio, score = scoring._calc_capacity(courier, order)
        assert ratio > 1.0
        assert score == 0.0

    def test_light_load_high_score(self):
        scoring = AIScoring.__new__(AIScoring)
        courier = MagicMock()
        courier.max_weight_kg = 50.0
        order = MagicMock()
        order.total_weight_kg = 5.0

        ratio, score = scoring._calc_capacity(courier, order)
        assert ratio < 0.2
        assert score > 0.9
