"""Tests unitaires pour le service de livraison."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.delivery.service import DeliveryService, VALID_TRANSITIONS
from src.delivery.models import OrderStatus


class TestValidTransitions:
    def test_draft_can_go_to_pending(self):
        assert OrderStatus.PENDING in VALID_TRANSITIONS[OrderStatus.DRAFT]

    def test_draft_cannot_go_to_delivered(self):
        assert OrderStatus.DELIVERED not in VALID_TRANSITIONS[OrderStatus.DRAFT]

    def test_assigned_can_go_to_courier_accepted(self):
        assert OrderStatus.COURIER_ACCEPTED in VALID_TRANSITIONS[OrderStatus.ASSIGNED]

    def test_in_transit_can_go_to_arriving(self):
        assert OrderStatus.ARRIVING in VALID_TRANSITIONS[OrderStatus.IN_TRANSIT]

    def test_completed_is_terminal(self):
        assert OrderStatus.COMPLETED not in VALID_TRANSITIONS or \
               len(VALID_TRANSITIONS.get(OrderStatus.COMPLETED, [])) == 0

    def test_all_statuses_have_entry(self):
        non_terminal = {
            OrderStatus.DRAFT, OrderStatus.PENDING, OrderStatus.ANALYZING,
            OrderStatus.READY_TO_ASSIGN, OrderStatus.ASSIGNING, OrderStatus.ASSIGNED,
            OrderStatus.COURIER_ACCEPTED, OrderStatus.PICKUP_IN_PROGRESS,
            OrderStatus.PICKED_UP, OrderStatus.IN_TRANSIT, OrderStatus.ARRIVING,
            OrderStatus.DELIVERED, OrderStatus.CONFIRMED,
            OrderStatus.COURIER_REFUSED, OrderStatus.EXPIRED,
            OrderStatus.DELIVERY_FAILED, OrderStatus.CANCELLED,
            OrderStatus.DISPUTED, OrderStatus.UNDER_REVIEW,
        }
        for status in non_terminal:
            assert status in VALID_TRANSITIONS, f"{status} missing from VALID_TRANSITIONS"


class TestReferenceGeneration:
    def test_reference_format(self):
        svc = DeliveryService.__new__(DeliveryService)
        ref = svc._generate_reference()
        assert ref.startswith("MMS-")
        assert len(ref) > 10
        parts = ref.split("-")
        assert len(parts) == 3
        assert len(parts[2]) == 6  # 6 hex chars


class TestTransitionValidation:
    @pytest.mark.asyncio
    async def test_invalid_transition_raises(self):
        db = AsyncMock()
        svc = DeliveryService(db)
        svc.repo = AsyncMock()

        order = MagicMock()
        order.id = MagicMock()
        order.status = OrderStatus.DRAFT
        order.company_id = MagicMock()
        svc.repo.get_order_by_id = AsyncMock(return_value=order)

        with pytest.raises(ValueError, match="Transition"):
            await svc.transition_status(
                order.id,
                order.company_id,
                OrderStatus.DELIVERED.value,
            )

    @pytest.mark.asyncio
    async def test_valid_transition_succeeds(self):
        db = AsyncMock()
        svc = DeliveryService(db)
        svc.repo = AsyncMock()

        order = MagicMock()
        order.id = MagicMock()
        order.status = OrderStatus.DRAFT
        order.company_id = MagicMock()
        svc.repo.get_order_by_id = AsyncMock(return_value=order)
        svc.repo.add_status_history = AsyncMock()

        result = await svc.transition_status(
            order.id,
            order.company_id,
            OrderStatus.PENDING.value,
        )

        assert order.status == OrderStatus.PENDING
        svc.repo.add_status_history.assert_called_once()
