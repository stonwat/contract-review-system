"""风险路由。"""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentAdmin
from app.core.deps import PaginationParams, get_pagination
from app.db.database import get_db
from app.models.risk_record import RiskRecord
from app.schemas.common import success
from app.schemas.risk import DismissRequest

router = APIRouter(prefix="/risks", tags=["风险"])


@router.get("")
async def list_risks(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination),
    risk_level: str | None = Query(None),
    dismissed: bool | None = Query(None),
) -> dict:
    """风险列表（分页）。"""
    stmt = select(RiskRecord)
    count_stmt = select(func.count(RiskRecord.id))
    if risk_level:
        stmt = stmt.where(RiskRecord.risk_level == risk_level)
        count_stmt = count_stmt.where(RiskRecord.risk_level == risk_level)
    if dismissed is not None:
        stmt = stmt.where(RiskRecord.dismissed == dismissed)
        count_stmt = count_stmt.where(RiskRecord.dismissed == dismissed)

    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(
        stmt.order_by(RiskRecord.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    )
    return success(
        {
            "items": [
                {
                    "id": str(r.id),
                    "contract_no": r.contract_no,
                    "risk_type": r.risk_type,
                    "risk_level": r.risk_level,
                    "source_type": r.source_type,
                    "detail": r.detail,
                    "dismissed": r.dismissed,
                }
                for r in result.scalars().all()
            ],
            "total": total,
            "page": pagination.page,
            "page_size": pagination.page_size,
        }
    )


@router.get("/summary")
async def risk_summary(db: AsyncSession = Depends(get_db)) -> dict:
    """风险汇总。"""
    result = await db.execute(select(RiskRecord))
    records = result.scalars().all()
    by_level = {"高": 0, "中": 0, "低": 0}
    for r in records:
        if not r.dismissed and r.risk_level in by_level:
            by_level[r.risk_level] += 1
    return success({"total": len(records), "by_level": by_level, "by_city": []})


@router.post("/{risk_id}/dismiss")
async def dismiss_risk(
    risk_id: UUID,
    body: DismissRequest,
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """人工忽略风险。"""
    risk = await db.get(RiskRecord, risk_id)
    if not risk:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "风险记录不存在")
    risk.dismissed = True
    risk.dismissed_by = body.dismissed_by or admin.username
    risk.dismissed_at = datetime.now(timezone.utc)
    await db.commit()
    return success({"id": str(risk.id), "dismissed": True})
