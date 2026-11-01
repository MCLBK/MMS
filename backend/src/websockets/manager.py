"""Gestionnaire de connexions WebSocket.

Gère les canaux :
  - user:{user_id}         — notifications personnelles
  - company:{company_id}   — événements entreprise (nouvelles commandes, etc.)
  - tracking:{company_id}  — positions GPS en temps réel
  - order:{order_id}       — suivi d'une commande spécifique
"""

import asyncio
import json
import logging
from datetime import UTC, datetime

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self._channels: dict[str, set[WebSocket]] = {}
        self._user_sockets: dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, channels: list[str], user_id: str | None = None):
        await websocket.accept()
        async with self._lock:
            for channel in channels:
                if channel not in self._channels:
                    self._channels[channel] = set()
                self._channels[channel].add(websocket)

            if user_id:
                if user_id not in self._user_sockets:
                    self._user_sockets[user_id] = set()
                self._user_sockets[user_id].add(websocket)

        logger.info(f"WS connected: channels={channels} user={user_id}")

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            for channel, sockets in list(self._channels.items()):
                sockets.discard(websocket)
                if not sockets:
                    del self._channels[channel]

            for user_id, sockets in list(self._user_sockets.items()):
                sockets.discard(websocket)
                if not sockets:
                    del self._user_sockets[user_id]

    async def broadcast(self, channel: str, event: str, data: dict):
        message = json.dumps(
            {
                "event": event,
                "data": data,
                "channel": channel,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )
        async with self._lock:
            sockets = list(self._channels.get(channel, set()))

        disconnected = []
        for ws in sockets:
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.append(ws)

        for ws in disconnected:
            await self.disconnect(ws)

    async def send_to_user(self, user_id: str, event: str, data: dict):
        message = json.dumps(
            {
                "event": event,
                "data": data,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )
        async with self._lock:
            sockets = list(self._user_sockets.get(user_id, set()))

        disconnected = []
        for ws in sockets:
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.append(ws)

        for ws in disconnected:
            await self.disconnect(ws)

    @property
    def stats(self) -> dict:
        return {
            "channels": len(self._channels),
            "total_connections": sum(len(s) for s in self._channels.values()),
            "users_online": len(self._user_sockets),
        }


manager = ConnectionManager()
