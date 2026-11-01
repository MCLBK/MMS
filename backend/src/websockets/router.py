"""Endpoints WebSocket pour notifications et tracking temps réel."""

import json
import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from src.websockets.manager import manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/notifications")
async def ws_notifications(
    websocket: WebSocket,
    user_id: str = Query(...),
    company_id: str = Query(None),
):
    channels = [f"user:{user_id}"]
    if company_id:
        channels.append(f"company:{company_id}")

    await manager.connect(websocket, channels, user_id=user_id)
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "ping":
                await websocket.send_text(json.dumps({"event": "pong"}))
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception:
        await manager.disconnect(websocket)


@router.websocket("/ws/tracking")
async def ws_tracking(
    websocket: WebSocket,
    company_id: str = Query(...),
):
    channels = [f"tracking:{company_id}"]
    await manager.connect(websocket, channels)
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "position_update":
                await manager.broadcast(
                    f"tracking:{company_id}",
                    "courier_position",
                    msg.get("data", {}),
                )
            elif msg.get("type") == "ping":
                await websocket.send_text(json.dumps({"event": "pong"}))
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception:
        await manager.disconnect(websocket)


@router.websocket("/ws/order/{order_id}")
async def ws_order_tracking(
    websocket: WebSocket,
    order_id: str,
):
    channels = [f"order:{order_id}"]
    await manager.connect(websocket, channels)
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "ping":
                await websocket.send_text(json.dumps({"event": "pong"}))
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception:
        await manager.disconnect(websocket)


@router.get("/ws/stats")
async def ws_stats():
    return manager.stats
