"""Émetteur d'événements temps réel vers les canaux WebSocket.

Utilisé par les services métier pour notifier les clients connectés.
"""

import uuid

from src.websockets.manager import manager


async def emit_order_created(company_id: uuid.UUID, order_data: dict):
    await manager.broadcast(
        f"company:{company_id}",
        "order_created",
        order_data,
    )


async def emit_order_status_changed(
    company_id: uuid.UUID,
    order_id: uuid.UUID,
    old_status: str,
    new_status: str,
    extra: dict | None = None,
):
    data = {
        "order_id": str(order_id),
        "old_status": old_status,
        "new_status": new_status,
        **(extra or {}),
    }
    await manager.broadcast(f"company:{company_id}", "order_status_changed", data)
    await manager.broadcast(f"order:{order_id}", "status_changed", data)


async def emit_courier_assigned(
    company_id: uuid.UUID,
    order_id: uuid.UUID,
    courier_id: uuid.UUID,
    courier_name: str,
    ai_score: float | None = None,
):
    data = {
        "order_id": str(order_id),
        "courier_id": str(courier_id),
        "courier_name": courier_name,
        "ai_score": ai_score,
    }
    await manager.broadcast(f"company:{company_id}", "courier_assigned", data)
    await manager.broadcast(f"order:{order_id}", "courier_assigned", data)


async def emit_courier_position(
    company_id: uuid.UUID,
    courier_id: uuid.UUID,
    latitude: float,
    longitude: float,
    speed_kmh: float | None = None,
    battery_level: int | None = None,
):
    await manager.broadcast(
        f"tracking:{company_id}",
        "courier_position",
        {
            "courier_id": str(courier_id),
            "latitude": latitude,
            "longitude": longitude,
            "speed_kmh": speed_kmh,
            "battery_level": battery_level,
        },
    )


async def emit_notification(user_id: uuid.UUID, notification_data: dict):
    await manager.send_to_user(str(user_id), "notification", notification_data)
