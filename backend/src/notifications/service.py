import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.notifications.repository import NotificationRepository


NOTIFICATION_TYPES = {
    "order_created": "Nouvelle commande",
    "order_assigned": "Commande attribuee",
    "courier_accepted": "Livreur en route",
    "delivery_completed": "Livraison terminee",
    "delivery_failed": "Echec de livraison",
    "status_changed": "Changement de statut",
    "system": "Systeme",
}


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = NotificationRepository(db)

    async def notify_user(
        self,
        user_id: uuid.UUID,
        type: str,
        title: str,
        body: str,
        data: dict | None = None,
    ):
        return await self.repo.create({
            "user_id": user_id,
            "type": type,
            "title": title,
            "body": body,
            "data": data,
        })

    async def notify_order_status_change(
        self,
        user_id: uuid.UUID,
        reference: str,
        old_status: str,
        new_status: str,
        order_id: uuid.UUID,
    ):
        return await self.notify_user(
            user_id=user_id,
            type="status_changed",
            title=f"Commande {reference}",
            body=f"Statut passe de {old_status} a {new_status}",
            data={"order_id": str(order_id), "old_status": old_status, "new_status": new_status},
        )

    async def notify_assignment(
        self,
        courier_user_id: uuid.UUID,
        reference: str,
        order_id: uuid.UUID,
    ):
        return await self.notify_user(
            user_id=courier_user_id,
            type="order_assigned",
            title="Nouvelle livraison",
            body=f"La commande {reference} vous a ete attribuee",
            data={"order_id": str(order_id)},
        )
