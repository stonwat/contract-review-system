"""项目路由：列表、详情、更新。"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentAdmin, PERMISSION_DENIED
from app.db.database import get_db
from app.models.project import Project
from app.schemas.common import success
from app.schemas.project import ProjectOut, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["项目管理"])


@router.get("")
async def list_projects(
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
    city: str | None = Query(None),
    audit_status: str | None = Query(None),
    llm_analyzed: bool | None = Query(None),
    project_risk: str | None = Query(None),
) -> dict:
    """项目列表。支持按地市、审查状态、分析状态、风险等级筛选。city_admin 可浏览全部但操作受限。"""
    stmt = select(Project)
    if city:
        stmt = stmt.where(Project.city == city)
    if audit_status:
        stmt = stmt.where(Project.audit_status == audit_status)
    if llm_analyzed is not None:
        stmt = stmt.where(Project.llm_analyzed == llm_analyzed)
    if project_risk:
        stmt = stmt.where(Project.project_risk == project_risk)

    projects = (await db.execute(stmt.order_by(Project.created_at.desc()))).scalars().all()
    items = [ProjectOut.model_validate(p).model_dump() for p in projects]
    return success({"items": items, "total": len(items)})


@router.get("/{contract_no}")
async def get_project(
    contract_no: str,
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """项目详情。"""
    project = await db.get(Project, contract_no)
    if not project:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "项目不存在")
    return success(ProjectOut.model_validate(project).model_dump())


@router.put("/{contract_no}")
async def update_project(
    contract_no: str,
    body: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """修正项目字段。可用于人工审查、更新风险等级、重置分析状态等。"""
    project = await db.get(Project, contract_no)
    if not project:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "项目不存在")

    # city_admin 只能操作自己地市的项目
    if not admin.check_city(project.city):
        raise PERMISSION_DENIED

    update_data = body.model_dump(exclude_unset=True)

    # 如果 audit_status 变为"已完成"，自动记录审查人和时间
    if update_data.get("audit_status") == "已完成":
        update_data["audited_by"] = admin.username if admin else None
        update_data["audited_at"] = datetime.now(timezone.utc)

    for field, value in update_data.items():
        setattr(project, field, value)

    await db.commit()
    return success({"contract_no": contract_no, "updated_at": str(project.updated_at)})
