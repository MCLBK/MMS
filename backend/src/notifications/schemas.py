import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class NotificationCreate(BaseModel):
    user_id: uuid.UUID
    type: str = Field(..., max_length=50)
    title: str = Field(..., max_length=200)
    body: str
    data: dict | None = None


class NotificationResponse(BaseModel):
    id: uuid.UUID
    type: str
    title: str
    body: str
    data: dict | None
    is_read: bool
    created_at: str

    model_config = {"from_attributes": True}


class NotificationList(BaseModel):
    items: list[NotificationResponse]
    unread_count: int
    total: int
