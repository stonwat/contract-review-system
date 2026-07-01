"""仪表盘路由。"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends

from app.db.database import get_db
from app.models.contract import Contract
from app.models.project import Project
from app.models.risk_record import RiskRecord
from app.schemas.common import success

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("/overview")
async def overview(db: AsyncSession = Depends(get_db)) -> dict:
    """总览：项目数、合同数、待确认数、高风险数、已完成数。"""
    project_count = (await db.execute(select(func.count(Project.contract_no)))).scalar_one()
    contract_count = (await db.execute(select(func.count(Contract.id)))).scalar_one()
    pending = (
        await db.execute(select(func.count(Contract.id)).where(Contract.verified == False))  # noqa: E712
    ).scalar_one()
    high_risk = (
        await db.execute(
            select(func.count(RiskRecord.id)).where(
                RiskRecord.risk_level == "高", RiskRecord.dismissed == False  # noqa: E712
            )
        )
    ).scalar_one()
    completed = (
        await db.execute(
            select(func.count(Project.contract_no)).where(Project.status == "已完成")
        )
    ).scalar_one()

    return success(
        {
            "project_count": project_count,
            "contract_count": contract_count,
            "pending_verify_count": pending,
            "high_risk_count": high_risk,
            "completed_count": completed,
        }
    )


@router.get("/city-stats")
async def city_stats(db: AsyncSession = Depends(get_db)) -> dict:
    """按地市统计。"""
    result = await db.execute(
        select(
            Project.city,
            func.count(Project.contract_no),
        ).group_by(Project.city)
    )
    stats = [
        {"city": row[0], "project_count": row[1], "high_risk": 0, "pending_verify": 0, "completed": 0}
        for row in result.all()
    ]
    return success(stats)
