"""JWT 认证与 RBAC 权限依赖。"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.database import get_db
from app.models.admin import Admin

# ── 错误定义 ──────────────────────────────────────────────

PERMISSION_DENIED = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="无权限执行此操作",
    headers={"X-Error-Code": "4003"},
)

UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="未提供认证信息",
    headers={"X-Error-Code": "4001"},
)


# ── AdminIdentity：轻量级身份对象，避免每次请求查库 ──────


@dataclass
class AdminIdentity:
    """从 JWT 解析出的管理员身份，不包含敏感字段（如 password_hash）。"""

    id: str
    username: str
    display_name: str | None
    role: str
    city: str | None
    is_active: bool

    @property
    def is_super_admin(self) -> bool:
        return self.role == "super_admin"

    @property
    def is_city_admin(self) -> bool:
        return self.role == "city_admin"

    @property
    def is_viewer(self) -> bool:
        return self.role == "viewer"

    @property
    def can_operate(self) -> bool:
        """是否可以执行修改/确认操作（viewer 不可）。"""
        return self.role != "viewer"

    def check_city(self, project_city: str | None) -> bool:
        """校验 city_admin 是否有权操作指定地市的项目。"""
        if self.is_super_admin:
            return True
        if self.is_city_admin:
            return project_city == self.city
        return False


# ── JWT 工具 ──────────────────────────────────────────────


def create_access_token(admin: Admin) -> str:
    """为管理员签发 JWT，payload 包含 role 与 city 以实现无状态鉴权。"""
    payload = {
        "sub": str(admin.id),
        "role": admin.role,
        "city": admin.city,
        "name": admin.display_name or admin.username,
        "exp": datetime.now(timezone.utc)
        + timedelta(hours=settings.jwt_expire_hours),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> dict:
    """解码并校验 JWT。"""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 已过期",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 Token",
        )


# ── 依赖注入 ──────────────────────────────────────────────


async def get_current_admin(
    authorization: Annotated[str | None, Header()] = None,
) -> AdminIdentity:
    """从 Authorization 头解析 JWT，返回 AdminIdentity（轻量身份，不查库）。"""
    if not authorization or not authorization.startswith("Bearer "):
        raise UNAUTHORIZED
    token = authorization.removeprefix("Bearer ")
    payload = decode_token(token)

    admin = AdminIdentity(
        id=payload.get("sub", ""),
        username=payload.get("name", ""),
        display_name=payload.get("name"),
        role=payload.get("role", "viewer"),
        city=payload.get("city"),
        is_active=True,
    )
    return admin


async def verify_agent_api_key(
    x_api_key: Annotated[str | None, Header()] = None,
) -> None:
    """Agent 客户端认证：校验 X-API-Key 头。"""
    if not x_api_key or x_api_key != settings.agent_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 Agent API Key",
        )


# ── 类型别名 ──────────────────────────────────────────────

CurrentAdmin = Annotated[AdminIdentity, Depends(get_current_admin)]
AgentAuth = Annotated[None, Depends(verify_agent_api_key)]


# ── 权限校验快捷函数 ──────────────────────────────────────


def require_role(*roles: str):
    """返回一个 FastAPI Depends 可用的权限检查依赖。

    用法：:

        @router.get(...)
        async def some_route(admin: AdminIdentity = Depends(require_role('super_admin'))):
            ...
    """

    async def _checker(admin: CurrentAdmin) -> AdminIdentity:
        if admin.role not in roles:
            raise PERMISSION_DENIED
        return admin

    return _checker


async def require_super_admin(admin: CurrentAdmin) -> AdminIdentity:
    """仅 super_admin 可访问。"""
    if not admin.is_super_admin:
        raise PERMISSION_DENIED
    return admin


SuperAdmin = Annotated[AdminIdentity, Depends(require_super_admin)]
