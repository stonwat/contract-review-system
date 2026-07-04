"""管理员 CRUD 路由（仅 super_admin 可访问）。"""

from uuid import UUID

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import SuperAdmin
from app.core.deps import PaginationParams, get_pagination
from app.db.database import get_db
from app.models.admin import Admin
from app.schemas.admin import (
    AdminCreateRequest,
    AdminOut,
    AdminUpdateRequest,
    ResetPasswordRequest,
)
from app.schemas.common import success

router = APIRouter(prefix="/admins", tags=["账号管理"])

CITIES = [
    "哈尔滨", "齐齐哈尔", "牡丹江", "佳木斯", "大庆",
    "鸡西", "双鸭山", "伊春", "七台河", "鹤岗",
    "黑河", "绥化", "大兴安岭",
]


# ── 校验助手 ──────────────────────────────────────────────


def _validate_role_city(role: str, city: str | None) -> None:
    """校验 role 与 city 的约束关系。"""
    if role not in ("super_admin", "city_admin", "viewer"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "无效的角色")
    if role == "city_admin":
        if not city:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "地市管理员必须指定地市")
        if city not in CITIES:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"无效的地市: {city}")
    else:
        if city is not None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "非地市管理员角色不能设置地市")


# ── 路由 ──────────────────────────────────────────────────


@router.get("")
async def list_admins(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination),
    admin: SuperAdmin = None,
) -> dict:
    """管理员列表（分页）。"""
    count_stmt = select(func.count(Admin.id))
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = (
        select(Admin)
        .order_by(Admin.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    )
    rows = (await db.execute(stmt)).scalars().all()
    items = [AdminOut.model_validate(r).model_dump() for r in rows]
    return success({"items": items, "total": total, "page": pagination.page, "page_size": pagination.page_size})


@router.post("")
async def create_admin(
    body: AdminCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = None,
) -> dict:
    """创建管理员。"""
    # 校验角色/地市约束
    _validate_role_city(body.role, body.city)

    # 查重
    existing = (await db.execute(select(Admin).where(Admin.username == body.username))).scalar_one_or_none()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, f"用户名 '{body.username}' 已存在")

    new_admin = Admin(
        username=body.username,
        password_hash=bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode(),
        display_name=body.display_name,
        role=body.role,
        city=body.city if body.role == "city_admin" else None,
        is_active=True,
    )
    db.add(new_admin)
    await db.commit()
    return success({"id": str(new_admin.id), "username": new_admin.username, "role": new_admin.role, "city": new_admin.city})


@router.put("/{admin_id}")
async def update_admin(
    admin_id: UUID,
    body: AdminUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = None,
) -> dict:
    """更新管理员信息（角色、地市、状态等）。"""
    admin_obj = await db.get(Admin, admin_id)
    if not admin_obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "管理员不存在")

    update_data = body.model_dump(exclude_unset=True)

    # 如果修改了 role，校验约束
    if "role" in update_data:
        new_role = update_data["role"]
        new_city = update_data.get("city", admin_obj.city)
        _validate_role_city(new_role, new_city)

    for field, value in update_data.items():
        setattr(admin_obj, field, value)

    await db.commit()
    return success({"id": str(admin_obj.id), "updated_at": str(admin_obj.updated_at)})


@router.post("/{admin_id}/reset-password")
async def reset_password(
    admin_id: UUID,
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = None,
) -> dict:
    """重置管理员密码。"""
    admin_obj = await db.get(Admin, admin_id)
    if not admin_obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "管理员不存在")

    admin_obj.password_hash = bcrypt.hashpw(body.new_password.encode(), bcrypt.gensalt()).decode()
    await db.commit()
    return success(message="密码重置成功")


@router.delete("/{admin_id}")
async def delete_admin(
    admin_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: SuperAdmin = None,
) -> dict:
    """删除管理员（不允许删除自己）。"""
    target = await db.get(Admin, admin_id)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "管理员不存在")
    if str(target.id) == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "不能删除自己的账号")

    await db.delete(target)
    await db.commit()
    return success(message="删除成功")
