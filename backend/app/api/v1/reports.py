"""报表路由。"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentAdmin, PERMISSION_DENIED
from app.db.database import get_db
from app.schemas.common import success
from app.services.report_generator import report_generator

router = APIRouter(prefix="/reports", tags=["报表"])


def _resolve_city(admin: CurrentAdmin, requested_city: str | None) -> str | None:
    """根据 admin 角色解析实际要查询的地市。city_admin 强制限定为自己地市。"""
    if admin.is_city_admin:
        return admin.city
    return requested_city


@router.get("/contract-consistency")
async def contract_consistency_report(
    city: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """报表一：合同内容一致性。city_admin 仅返回自己地市数据。"""
    filtered_city = _resolve_city(admin, city)
    return success(await report_generator.contract_consistency_report(db, filtered_city))


@router.get("/acceptance-consistency")
async def acceptance_consistency_report(
    city: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """报表二：验收报告一致性。city_admin 仅返回自己地市数据。"""
    filtered_city = _resolve_city(admin, city)
    return success(await report_generator.acceptance_consistency_report(db, filtered_city))


@router.get("/low-margin")
async def low_margin_report(
    city: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """报表三：低毛利项目。city_admin 仅返回自己地市数据。"""
    filtered_city = _resolve_city(admin, city)
    return success(await report_generator.low_margin_report(db, filtered_city))


@router.get("/high-risk")
async def high_risk_report(
    city: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """报表四：高风险项目。city_admin 仅返回自己地市数据。"""
    filtered_city = _resolve_city(admin, city)
    return success(await report_generator.high_risk_report(db, filtered_city))


@router.get("/export")
async def export_report(
    report_type: str = Query(
        ...,
        description="报表类型: contract-consistency / acceptance-consistency / low-margin / high-risk",
    ),
    city: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> StreamingResponse:
    """导出为 Excel。viewer 不可导出。"""
    if not admin.can_operate:
        raise PERMISSION_DENIED
    filtered_city = _resolve_city(admin, city)
    output = await report_generator.export_excel(db, report_type, filtered_city)
    filename = f"{report_type}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
