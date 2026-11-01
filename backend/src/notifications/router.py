import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_current_active_user
from src.database.base import get_db
from src.notifications.repository import NotificationRepository
from src.notifications.schemas import NotificationList, NotificationResponse
from src.users.models import User

router = APIRouter()


@router.get("/notifications", response_model=NotificationList)
async def list_notifications(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
):
    repo = NotificationRepository(db)
    notifications, unread_count, total = await repo.get_by_user(
        user_id=current_user.id,
        offset=(page - 1) * page_size,
        limit=page_size,
        unread_only=unread_only,
    )
    return NotificationList(
        items=[
            NotificationResponse(
                id=n.id,
                type=n.type,
                title=n.title,
                body=n.body,
                data=n.data,
                is_read=n.is_read,
                created_at=n.created_at.isoformat(),
            )
            for n in notifications
        ],
        unread_count=unread_count,
        total=total,
    )


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = NotificationRepository(db)
    await repo.mark_read(notification_id, current_user.id)
    await db.commit()
    return {"status": "ok"}


@router.post("/notifications/read-all")
async def mark_all_read(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = NotificationRepository(db)
    count = await repo.mark_all_read(current_user.id)
    await db.commit()
    return {"status": "ok", "marked": count}
