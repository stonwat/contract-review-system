"""认证路由：管理员登录。"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import bcrypt
from app.config import settings
from app.db.database import get_db
from app.core.auth import create_access_token
from app.models.admin import Admin
from app.schemas.auth import AdminInfo, LoginRequest, LoginResponse
from app.schemas.common import success

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> dict:
    """管理员登录，返回 JWT。"""
    result = await db.execute(select(Admin).where(Admin.username == body.username))
    admin = result.scalar_one_or_none()

    if not admin or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    if not bcrypt.checkpw(body.password.encode(), admin.password_hash.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    token = create_access_token(str(admin.id))
    return success(
        {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.jwt_expire_hours * 3600,
            "admin": AdminInfo.model_validate(admin).model_dump(),
        }
    )
