"""JWT 认证依赖。"""

from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.database import get_db
from app.models.admin import Admin


def create_access_token(admin_id: str) -> str:
    """为管理员签发 JWT。"""
    payload = {
        "sub": str(admin_id),
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


async def get_current_admin(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> Admin:
    """从 Authorization 头解析 JWT 并返回当前管理员。"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证信息",
        )
    token = authorization.removeprefix("Bearer ")
    payload = decode_token(token)
    admin_id = payload.get("sub")

    result = await db.execute(select(Admin).where(Admin.id == admin_id))
    admin = result.scalar_one_or_none()
    if not admin or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="管理员不存在或已被禁用",
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


CurrentAdmin = Annotated[Admin, Depends(get_current_admin)]
AgentAuth = Annotated[None, Depends(verify_agent_api_key)]
