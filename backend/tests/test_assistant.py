"""Tests unitaires pour l'assistant IA."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.ai.assistant import AIAssistant


class TestTemplateResponses:
    @pytest.mark.asyncio
    async def test_greeting_response(self):
        db = AsyncMock()
        assistant = AIAssistant(db)
        assistant._get_status_summary = AsyncMock(return_value={"pending": 5, "in_transit": 3})
        assistant._check_ollama = AsyncMock(return_value=False)

        resp = await assistant.chat(MagicMock(), "Bonjour !")
        assert "bonjour" in resp.message.lower() or "assistant" in resp.message.lower()
        assert resp.source == "template-engine"

    @pytest.mark.asyncio
    async def test_stats_response(self):
        db = AsyncMock()
        assistant = AIAssistant(db)
        assistant._get_status_summary = AsyncMock(
            return_value={"pending": 5, "in_transit": 3, "completed": 12}
        )
        assistant._check_ollama = AsyncMock(return_value=False)

        resp = await assistant.chat(MagicMock(), "Combien de commandes ?")
        assert "20" in resp.message  # 5+3+12 = 20
        assert resp.source == "template-engine"

    @pytest.mark.asyncio
    async def test_problem_response(self):
        db = AsyncMock()
        assistant = AIAssistant(db)
        assistant._get_status_summary = AsyncMock(
            return_value={"delivery_failed": 3, "in_transit": 5}
        )
        assistant._check_ollama = AsyncMock(return_value=False)

        resp = await assistant.chat(MagicMock(), "Y a-t-il des problèmes ?")
        assert "3" in resp.message
        assert (
            "échec" in resp.message.lower()
            or "erreur" in resp.message.lower()
            or "réassigner" in resp.message.lower()
        )

    @pytest.mark.asyncio
    async def test_optimization_tips(self):
        db = AsyncMock()
        assistant = AIAssistant(db)
        assistant._get_status_summary = AsyncMock(return_value={})
        assistant._check_ollama = AsyncMock(return_value=False)

        resp = await assistant.chat(MagicMock(), "Comment optimiser mes livraisons ?")
        assert "optimisation" in resp.message.lower() or "conseil" in resp.message.lower()

    @pytest.mark.asyncio
    async def test_suggestions_always_present(self):
        db = AsyncMock()
        assistant = AIAssistant(db)
        assistant._get_status_summary = AsyncMock(return_value={})
        assistant._check_ollama = AsyncMock(return_value=False)

        resp = await assistant.chat(MagicMock(), "test")
        assert len(resp.suggestions) > 0
        assert len(resp.suggestions) <= 3


class TestContextGathering:
    @pytest.mark.asyncio
    async def test_focus_detection_orders(self):
        db = AsyncMock()
        assistant = AIAssistant(db)
        assistant._get_status_summary = AsyncMock(return_value={})

        ctx = await assistant._gather_context(MagicMock(), "Où en sont mes commandes ?")
        assert ctx["focus"] == "orders"

    @pytest.mark.asyncio
    async def test_focus_detection_couriers(self):
        db = AsyncMock()
        assistant = AIAssistant(db)
        assistant._get_status_summary = AsyncMock(return_value={})

        ctx = await assistant._gather_context(MagicMock(), "Performance des livreurs")
        assert ctx["focus"] == "couriers"

    @pytest.mark.asyncio
    async def test_focus_detection_general(self):
        db = AsyncMock()
        assistant = AIAssistant(db)
        assistant._get_status_summary = AsyncMock(return_value={})

        ctx = await assistant._gather_context(MagicMock(), "Bonjour")
        assert ctx["focus"] == "general"
