"""比对路由。"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentAdmin
from app.db.database import get_db
from app.models.comparison import Comparison
from app.models.line_item_comparison import LineItemComparison
from app.schemas.common import success
from app.schemas.comparison import ComparisonCreate

router = APIRouter(prefix="/comparisons", tags=["合同比对"])


@router.post("")
async def create_comparison(
    body: ComparisonCreate,
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """触发比对（异步执行，此处返回 processing 状态）。"""
    comparison = Comparison(
        front_contract_id=body.front_contract_id,
        back_contract_id=body.back_contract_id,
    )
    db.add(comparison)
    await db.commit()
    # TODO: 投递到 arq 队列异步执行比对引擎
    return success(
        {"comparison_id": str(comparison.id), "status": "processing"}
    )


@router.post("/auto")
async def auto_compare(
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """自动检测可配对但未比对的合同，批量执行。"""
    # 骨架：实际需查询同一 contract_no 下已确认但未比对的前后项对
    return success({"total_pairs": 0, "new_comparisons": 0, "existed": 0})


@router.get("")
async def list_comparisons(db: AsyncSession = Depends(get_db)) -> dict:
    """比对结果列表。"""
    result = await db.execute(select(Comparison))
    return success({"items": [str(c.id) for c in result.scalars().all()]})


@router.get("/{comparison_id}")
async def get_comparison(
    comparison_id: UUID, db: AsyncSession = Depends(get_db)
) -> dict:
    """比对详情（含分项比对明细）。"""
    comparison = await db.get(Comparison, comparison_id)
    if not comparison:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "比对记录不存在")

    items_result = await db.execute(
        select(LineItemComparison).where(
            LineItemComparison.comparison_id == comparison_id
        )
    )
    return success({"comparison_id": str(comparison_id)})
