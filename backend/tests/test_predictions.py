"""Tests unitaires pour le service de prédictions."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from src.ai.predictions import (
    DeliveryTimePrediction,
    VolumeForecast,
    HotZone,
    RiskAssessment,
    PredictionService,
)
from src.delivery.models import OrderPriority


class TestDeliveryTimePrediction:
    @pytest.mark.asyncio
    async def test_basic_prediction(self):
        db = AsyncMock()
        # Mock _get_historical_avg_time to return None
        svc = PredictionService(db)
        svc._get_historical_avg_time = AsyncMock(return_value=None)

        pred = await svc.predict_delivery_time(
            company_id=MagicMock(),
            pickup_lat=5.3484,
            pickup_lng=-4.0167,
            delivery_lat=5.3600,
            delivery_lng=-4.0000,
        )

        assert isinstance(pred, DeliveryTimePrediction)
        assert pred.estimated_minutes >= 10
        assert 0 < pred.confidence <= 1.0
        assert "distance_km" in pred.factors

    @pytest.mark.asyncio
    async def test_no_coordinates_still_works(self):
        db = AsyncMock()
        svc = PredictionService(db)
        svc._get_historical_avg_time = AsyncMock(return_value=None)

        pred = await svc.predict_delivery_time(
            company_id=MagicMock(),
            pickup_lat=None,
            pickup_lng=None,
            delivery_lat=None,
            delivery_lng=None,
        )

        assert pred.estimated_minutes >= 10

    @pytest.mark.asyncio
    async def test_urgent_priority_faster(self):
        db = AsyncMock()
        svc = PredictionService(db)
        svc._get_historical_avg_time = AsyncMock(return_value=None)

        normal = await svc.predict_delivery_time(
            company_id=MagicMock(),
            pickup_lat=5.35, pickup_lng=-4.02,
            delivery_lat=5.38, delivery_lng=-3.98,
            priority="normal",
        )
        urgent = await svc.predict_delivery_time(
            company_id=MagicMock(),
            pickup_lat=5.35, pickup_lng=-4.02,
            delivery_lat=5.38, delivery_lng=-3.98,
            priority="urgent",
        )

        assert urgent.estimated_minutes <= normal.estimated_minutes


class TestRiskAssessment:
    @pytest.mark.asyncio
    async def test_low_risk_order(self):
        db = AsyncMock()
        svc = PredictionService(db)
        svc._get_zone_failure_rate = AsyncMock(return_value=None)

        order = MagicMock()
        order.priority = OrderPriority.NORMAL
        order.total_weight_kg = 5.0
        order.items = []
        order.pickup_lat = 5.35
        order.pickup_lng = -4.02
        order.delivery_lat = 5.36
        order.delivery_lng = -4.01

        risk = await svc.assess_delivery_risk(MagicMock(), order)

        assert isinstance(risk, RiskAssessment)
        assert risk.risk_level in ("low", "medium")
        assert len(risk.recommendations) > 0

    @pytest.mark.asyncio
    async def test_high_risk_heavy_fragile(self):
        db = AsyncMock()
        svc = PredictionService(db)
        svc._get_zone_failure_rate = AsyncMock(return_value=0.20)

        order = MagicMock()
        order.priority = OrderPriority.URGENT
        order.total_weight_kg = 60.0
        item = MagicMock()
        item.is_fragile = True
        order.items = [item]
        order.pickup_lat = 5.35
        order.pickup_lng = -4.02
        order.delivery_lat = 5.60
        order.delivery_lng = -3.80

        risk = await svc.assess_delivery_risk(MagicMock(), order)

        assert risk.risk_score >= 0.4
        assert risk.risk_level in ("high", "critical")
        assert len(risk.factors) >= 3


class TestHotZoneDetection:
    @pytest.mark.asyncio
    async def test_empty_data_returns_empty(self):
        db = AsyncMock()
        mock_result = MagicMock()
        mock_result.all.return_value = []
        db.execute = AsyncMock(return_value=mock_result)

        svc = PredictionService(db)
        zones = await svc.detect_hot_zones(MagicMock(), days=7)
        assert zones == []
