"""报表路由。"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentAdmin
from app.db.database import get_db
from app.schemas.common import success
from app.services.report_generator import report_generator

router = APIRouter(prefix="/reports", tags=["报表"])


@router.get("/contract-consistency")
async def contract_consistency(
    city: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """合同内容一致性报表。"""
    return success(await report_generator.contract_consistency(db, city))


@router.get("/acceptance-consistency")
async def acceptance_consistency(
    city: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """验收报告一致性报表。"""
    return success({"summary": [], "details": []})


@router.get("/low-margin")
async def low_margin(
    threshold: float = Query(0.03),
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """低毛利项目报表。"""
    return success(await report_generator.low_margin(db, threshold))


@router.get("/high-risk")
async def high_risk(
    db: AsyncSession = Depends(get_db), admin: CurrentAdmin = None
) -> dict:
    """高风险项目报表（三条件交集）。"""
    return success(await report_generator.high_risk(db))


@router.get("/export")
async def export_report(
    report_type: str = Query(...),
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> StreamingResponse:
    """导出为 Excel。骨架，实际实现用 openpyxl 生成。"""
    from io import BytesIO

    output = BytesIO()
    output.write(b"placeholder")
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={report_type}.xlsx"},
    )
