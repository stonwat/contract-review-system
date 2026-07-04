"""管理员管理 schema。"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AdminOut(BaseModel):
    """管理员列表/详情响应。"""
    id: UUID
    username: str
    display_name: str | None = None
    role: str = "viewer"
    city: str | None = None
    is_active: bool = True
    created_at: datetime | None = None  # Pydantic auto-serializes datetime to ISO string

    model_config = {"from_attributes": True}


class AdminCreateRequest(BaseModel):
    """创建管理员请求。"""
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=6, max_length=100)
    display_name: str | None = None
    role: str = Field(default="viewer", pattern=r"^(super_admin|city_admin|viewer)$")
    city: str | None = None


class AdminUpdateRequest(BaseModel):
    """更新管理员请求（所有字段可选）。"""
    display_name: str | None = None
    role: str | None = Field(None, pattern=r"^(super_admin|city_admin|viewer)$")
    city: str | None = None
    is_active: bool | None = None


class ResetPasswordRequest(BaseModel):
    """重置密码请求。"""
    new_password: str = Field(..., min_length=6, max_length=100)
