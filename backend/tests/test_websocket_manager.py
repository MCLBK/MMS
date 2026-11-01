"""Tests unitaires pour le gestionnaire WebSocket."""

from unittest.mock import AsyncMock

import pytest

from src.websockets.manager import ConnectionManager


class TestConnectionManager:
    @pytest.mark.asyncio
    async def test_connect_and_stats(self):
        mgr = ConnectionManager()
        ws = AsyncMock()
        ws.send_text = AsyncMock()

        await mgr.connect(ws, ["company:abc"], user_id="user1")

        assert mgr.stats["channels"] == 1
        assert mgr.stats["total_connections"] == 1
        assert mgr.stats["users_online"] == 1

    @pytest.mark.asyncio
    async def test_disconnect_removes(self):
        mgr = ConnectionManager()
        ws = AsyncMock()

        await mgr.connect(ws, ["company:abc"], user_id="user1")
        await mgr.disconnect(ws)

        assert mgr.stats["channels"] == 0
        assert mgr.stats["users_online"] == 0

    @pytest.mark.asyncio
    async def test_broadcast_sends_to_channel(self):
        mgr = ConnectionManager()
        ws1 = AsyncMock()
        ws2 = AsyncMock()

        await mgr.connect(ws1, ["company:abc"])
        await mgr.connect(ws2, ["company:abc"])

        await mgr.broadcast("company:abc", "test_event", {"key": "value"})

        assert ws1.send_text.call_count == 1
        assert ws2.send_text.call_count == 1

    @pytest.mark.asyncio
    async def test_broadcast_different_channel_ignored(self):
        mgr = ConnectionManager()
        ws1 = AsyncMock()
        ws2 = AsyncMock()

        await mgr.connect(ws1, ["company:abc"])
        await mgr.connect(ws2, ["company:xyz"])

        await mgr.broadcast("company:abc", "test_event", {"key": "value"})

        assert ws1.send_text.call_count == 1
        assert ws2.send_text.call_count == 0

    @pytest.mark.asyncio
    async def test_send_to_user(self):
        mgr = ConnectionManager()
        ws = AsyncMock()

        await mgr.connect(ws, ["company:abc"], user_id="user1")
        await mgr.send_to_user("user1", "notification", {"text": "hello"})

        assert ws.send_text.call_count == 1

    @pytest.mark.asyncio
    async def test_send_to_unknown_user_no_error(self):
        mgr = ConnectionManager()
        await mgr.send_to_user("unknown", "test", {})

    @pytest.mark.asyncio
    async def test_broken_socket_auto_cleanup(self):
        mgr = ConnectionManager()
        ws = AsyncMock()
        ws.send_text = AsyncMock(side_effect=Exception("broken pipe"))

        await mgr.connect(ws, ["ch:1"], user_id="u1")
        await mgr.broadcast("ch:1", "event", {})

        assert mgr.stats["total_connections"] == 0

    @pytest.mark.asyncio
    async def test_multiple_channels(self):
        mgr = ConnectionManager()
        ws = AsyncMock()

        await mgr.connect(ws, ["ch:1", "ch:2", "ch:3"])

        assert mgr.stats["channels"] == 3
        assert mgr.stats["total_connections"] == 3
