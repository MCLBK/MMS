import uuid

from pydantic import BaseModel, Field

from src.schemas.common import BaseSchema


class UserListItem(BaseSchema):
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    phone: str | None
    is_active: bool
    is_verified: bool
    is_super_admin: bool


class UserDetail(UserListItem):
    avatar_url: str | None
    created_at: str
    memberships: list["MembershipInfo"] = []


class MembershipInfo(BaseSchema):
    company_id: uuid.UUID
    company_name: str
    role_name: str
    is_active: bool


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    is_active: bool | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


UserDetail.model_rebuild()
