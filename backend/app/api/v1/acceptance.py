"""验收报告路由。"""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AgentAuth, CurrentAdmin, PERMISSION_DENIED
from app.core.deps import PaginationParams, get_pagination
from app.db.database import get_db
from app.models.acceptance_report import AcceptanceReport
from app.models.project import Project
from app.schemas.acceptance import (
    AcceptanceCreate,
    AcceptanceListItem,
    AcceptanceOut,
    AcceptanceUpdate,
    VerifyAcceptanceRequest,
)
from app.schemas.common import success

router = APIRouter(prefix="/acceptance", tags=["验收报告"])


def _update_has_flag(project: Project, acceptance_type: str | None, value: bool) -> None:
    """根据验收类型更新 projects 表对应的 has_* 布尔标记。"""
    if acceptance_type == "前项":
        project.has_front_acceptance = value
    elif acceptance_type == "后项":
        project.has_back_acceptance = value


async def _get_project_city(contract_no: str, db: AsyncSession) -> str | None:
    """通过 contract_no 获取项目地市。"""
    project = await db.get(Project, contract_no)
    return project.city if project else None


@router.get("/check")
async def check_duplicate(
    contract_no: str = Query(..., description="合同编号"),
    acceptance_type: str = Query(..., description="验收类型：前项/后项"),
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """Agent 插入前去重检查：同编号同类型验收报告是否已存在。"""
    existing = (await db.execute(
        select(AcceptanceReport).where(
            AcceptanceReport.contract_no == contract_no,
            AcceptanceReport.acceptance_type == acceptance_type,
        )
    )).scalars().first()

    return success({"exists": existing is not None})


@router.post("")
async def create_acceptance(
    body: AcceptanceCreate,
    db: AsyncSession = Depends(get_db),
    _: AgentAuth = None,
) -> dict:
    """Agent 推送验收报告提取结果。后端自动维护 projects.has_* 标记。"""
    report = AcceptanceReport(
        acceptance_no=body.acceptance_no,
        contract_no=body.contract_no,
        acceptance_type=body.acceptance_type,
        type_judge_basis=body.type_judge_basis,
        acceptance_content=body.acceptance_content,
        acceptance_date=body.acceptance_date,
        acceptance_result=body.acceptance_result,
        source_file_name=body.source_file_name,
        extracted_at=datetime.now(timezone.utc),
    )
    db.add(report)
    await db.flush()

    # 维护 projects 表的 has_* 布尔标记
    project = await db.get(Project, body.contract_no)
    if project:
        _update_has_flag(project, body.acceptance_type, True)

    await db.commit()
    return success({"acceptance_id": str(report.id)})


@router.get("/{report_id}")
async def get_acceptance(
    report_id: UUID, db: AsyncSession = Depends(get_db), admin: CurrentAdmin = None
) -> dict:
    """验收详情。"""
    report = await db.get(AcceptanceReport, report_id)
    if not report:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "验收报告不存在")
    data = AcceptanceOut.model_validate(report).model_dump()
    return success(data)


@router.get("")
async def list_acceptance(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination),
    admin: CurrentAdmin = None,
    contract_no: str | None = Query(None),
    verified: bool | None = Query(None),
) -> dict:
    """验收报告列表（分页）。"""
    stmt = select(AcceptanceReport)
    count_stmt = select(func.count(AcceptanceReport.id))

    if contract_no:
        stmt = stmt.where(AcceptanceReport.contract_no.ilike(f"%{contract_no}%"))
        count_stmt = count_stmt.where(AcceptanceReport.contract_no.ilike(f"%{contract_no}%"))
    if verified is not None:
        stmt = stmt.where(AcceptanceReport.verified == verified)
        count_stmt = count_stmt.where(AcceptanceReport.verified == verified)

    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(
        stmt.order_by(AcceptanceReport.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    )
    reports = result.scalars().all()
    items = [AcceptanceListItem.model_validate(r).model_dump() for r in reports]
    return success(
        {
            "items": items,
            "total": total,
            "page": pagination.page,
            "page_size": pagination.page_size,
        }
    )


@router.put("/{report_id}")
async def update_acceptance(
    report_id: UUID,
    body: AcceptanceUpdate,
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """修正验收报告。"""
    report = await db.get(AcceptanceReport, report_id)
    if not report:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "验收报告不存在")

    city = await _get_project_city(report.contract_no, db)
    if not admin.check_city(city):
        raise PERMISSION_DENIED

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(report, field, value)
    await db.commit()
    return success({"id": str(report.id)})


@router.post("/{report_id}/verify")
async def verify_acceptance(
    report_id: UUID,
    body: VerifyAcceptanceRequest,
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """人工确认验收报告。city_admin 只能确认自己地市的验收报告。"""
    report = await db.get(AcceptanceReport, report_id)
    if not report:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "验收报告不存在")

    city = await _get_project_city(report.contract_no, db)
    if not admin.check_city(city):
        raise PERMISSION_DENIED

    report.verified = True
    report.verified_by = body.verified_by or admin.username
    report.verified_at = datetime.now(timezone.utc)
    await db.commit()
    return success({"id": str(report.id), "verified": True})


@router.delete("/{report_id}")
async def delete_acceptance(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """删除验收报告。仅 super_admin 可删除。删除后回置 projects 表对应的 has_* 标记。"""
    if not admin.is_super_admin:
        raise PERMISSION_DENIED

    report = await db.get(AcceptanceReport, report_id)
    if not report:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "验收报告不存在")
    contract_no = report.contract_no
    acceptance_type = report.acceptance_type
    await db.delete(report)
    await db.flush()

    project = await db.get(Project, contract_no)
    if project:
        remaining = (await db.execute(
            select(AcceptanceReport).where(
                AcceptanceReport.contract_no == contract_no,
                AcceptanceReport.acceptance_type == acceptance_type,
            )
        )).scalars().all()
        if not remaining:
            _update_has_flag(project, acceptance_type, False)

    await db.commit()
    return success(message="删除成功")
