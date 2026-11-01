import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class IDResponse(BaseSchema):
    id: uuid.UUID


class MessageResponse(BaseSchema):
    message: str


class PaginatedParams(BaseModel):
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseSchema):
    total: int
    page: int
    page_size: int
    total_pages: int
