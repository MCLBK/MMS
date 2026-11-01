import uuid
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    user_id: uuid.UUID | None
    company_id: uuid.UUID | None
    action: str
    resource_type: str
    resource_id: uuid.UUID | None
    details: dict | None
    ip_address: str | None
    created_at: str

    model_config = {"from_attributes": True}


class PaginatedAuditLogs(BaseModel):
    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int
