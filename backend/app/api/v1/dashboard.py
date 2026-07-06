"""仪表盘路由。"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends

from app.core.auth import CurrentAdmin
from app.db.database import get_db
from app.models.contract import Contract
from app.models.project import Project
from app.schemas.common import success

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("/overview")
async def overview(
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """总览：项目数、合同数、待确认数、高风险数、已完成数、已分析数。city_admin 仅看自己地市。"""

    def _filter(project_q):
        """city_admin 只统计自己地市的项目。"""
        if admin and admin.is_city_admin:
            return project_q.where(Project.city == admin.city)
        return project_q

    def _contract_filter(stmt):
        """city_admin 只统计自己地市的合同（通过 project.city 关联）。"""
        if admin and admin.is_city_admin:
            return stmt.join(Project, Contract.contract_no == Project.contract_no).where(Project.city == admin.city)
        return stmt

    project_count = (await db.execute(
        _filter(select(func.count(Project.contract_no)))
    )).scalar_one()
    contract_count = (await db.execute(
        _contract_filter(select(func.count(Contract.id)))
    )).scalar_one()
    pending = (
        await db.execute(select(func.count(Contract.id)).where(Contract.verified == False))  # noqa: E712
    ).scalar_one()
    completed = (
        await db.execute(
            _filter(select(func.count(Project.contract_no)).where(Project.audit_status == "已完成"))
        )
    ).scalar_one()
    high_risk = (
        await db.execute(
            _filter(select(func.count(Project.contract_no)).where(Project.project_risk == "高风险"))
        )
    ).scalar_one()
    llm_analyzed = (
        await db.execute(
            _filter(select(func.count(Project.contract_no)).where(Project.llm_analyzed == True))  # noqa: E712
        )
    ).scalar_one()

    # 前后项数量
    front_count = (
        await db.execute(
            _contract_filter(
                select(func.count(func.distinct(Contract.contract_no)))
                .where(Contract.contract_type == "前项")
            )
        )
    ).scalar_one()
    back_count = (
        await db.execute(
            _contract_filter(
                select(func.count(func.distinct(Contract.contract_no)))
                .where(Contract.contract_type == "后项")
            )
        )
    ).scalar_one()
    # 四材料齐全的项目数（具备分析条件）
    ready_count = (
        await db.execute(
            _filter(select(func.count(Project.contract_no)).where(
                Project.has_front_contract == True,  # noqa: E712
                Project.has_back_contract == True,  # noqa: E712
                Project.has_front_acceptance == True,  # noqa: E712
                Project.has_back_acceptance == True,  # noqa: E712
            ))
        )
    ).scalar_one()

    return success(
        {
            "project_count": project_count,
            "contract_count": contract_count,
            "pending_verify_count": pending,
            "completed_count": completed,
            "high_risk_count": high_risk,
            "llm_analyzed_count": llm_analyzed,
            "front_count": front_count,
            "back_count": back_count,
            "ready_count": ready_count,
        }
    )


@router.get("/city-stats")
async def city_stats(
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """按地市统计。city_admin 仅返回自己地市。"""
    base_q = (
        select(
            Project.city,
            func.count(Project.contract_no).label("project_count"),
        )
        .group_by(Project.city)
    )
    if admin and admin.is_city_admin:
        base_q = base_q.where(Project.city == admin.city)
    base_result = await db.execute(base_q)
    base_stats = {
        row[0]: {
            "city": row[0],
            "project_count": row[1],
            "pending_verify": 0,
            "completed": 0,
            "high_risk": 0,
        }
        for row in base_result.all()
    }

    # 待确认合同数（按城市）
    pending_q = (
        select(
            Project.city,
            func.count(Contract.id),
        )
        .join(Contract, Contract.contract_no == Project.contract_no)
        .where(Contract.verified == False)  # noqa: E712
        .group_by(Project.city)
    )
    if admin and admin.is_city_admin:
        pending_q = pending_q.where(Project.city == admin.city)
    pending_result = await db.execute(pending_q)
    for row in pending_result.all():
        if row[0] in base_stats:
            base_stats[row[0]]["pending_verify"] = row[1]

    # 已完成项目数（按城市）
    completed_q = (
        select(
            Project.city,
            func.count(Project.contract_no),
        )
        .where(Project.audit_status == "已完成")
        .group_by(Project.city)
    )
    if admin and admin.is_city_admin:
        completed_q = completed_q.where(Project.city == admin.city)
    completed_result = await db.execute(completed_q)
    for row in completed_result.all():
        if row[0] in base_stats:
            base_stats[row[0]]["completed"] = row[1]

    # 高风险项目数（按城市）
    high_risk_q = (
        select(
            Project.city,
            func.count(Project.contract_no),
        )
        .where(Project.project_risk == "高风险")
        .group_by(Project.city)
    )
    if admin and admin.is_city_admin:
        high_risk_q = high_risk_q.where(Project.city == admin.city)
    high_risk_result = await db.execute(high_risk_q)
    for row in high_risk_result.all():
        if row[0] in base_stats:
            base_stats[row[0]]["high_risk"] = row[1]

    return success(list(base_stats.values()))
