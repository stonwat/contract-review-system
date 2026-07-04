"""验收报告对比分析路由：Agent UPSERT、查询、人工确认。"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AgentAuth, CurrentAdmin, PERMISSION_DENIED
from app.db.database import get_db
from app.models.acceptance_report_analysis import AcceptanceReportAnalysis
from app.models.project import Project
from app.schemas.analysis import AcceptanceAnalysisCreate, AcceptanceAnalysisOut, VerifyAnalysisRequest
from app.schemas.common import success

router = APIRouter(prefix="/acceptance-analysis", tags=["验收分析"])


@router.post("")
async def upsert_acceptance_analysis(
    body: AcceptanceAnalysisCreate,
    db: AsyncSession = Depends(get_db),
    _: AgentAuth = None,
) -> dict:
    """Agent 推送验收报告对比分析结果。UPSERT：存在则更新，不存在则创建。"""
    existing = (await db.execute(
        select(AcceptanceReportAnalysis).where(
            AcceptanceReportAnalysis.contract_no == body.contract_no
        )
    )).scalars().first()

    if existing:
        existing.similarity = body.similarity
        existing.analysis = body.analysis
        analysis = existing
    else:
        analysis = AcceptanceReportAnalysis(
            contract_no=body.contract_no,
            similarity=body.similarity,
            analysis=body.analysis,
        )
        db.add(analysis)

    await db.commit()
    return success({"id": str(analysis.id), "contract_no": body.contract_no})


@router.get("/{contract_no}")
async def get_acceptance_analysis(
    contract_no: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """查询单个项目的验收报告分析结果。"""
    analysis = (await db.execute(
        select(AcceptanceReportAnalysis).where(
            AcceptanceReportAnalysis.contract_no == contract_no
        )
    )).scalars().first()
    if not analysis:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "分析结果不存在")
    return success(AcceptanceAnalysisOut.model_validate(analysis).model_dump())


@router.get("")
async def list_acceptance_analysis(
    db: AsyncSession = Depends(get_db),
    verified: bool | None = Query(None),
) -> dict:
    """验收报告分析结果列表。"""
    stmt = select(AcceptanceReportAnalysis)
    if verified is not None:
        stmt = stmt.where(AcceptanceReportAnalysis.verified == verified)
    rows = (await db.execute(stmt.order_by(AcceptanceReportAnalysis.created_at.desc()))).scalars().all()
    items = [AcceptanceAnalysisOut.model_validate(r).model_dump() for r in rows]
    return success({"items": items, "total": len(items)})


@router.post("/{contract_no}/verify")
async def verify_acceptance_analysis(
    contract_no: str,
    body: VerifyAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """人工确认验收报告分析结果。city_admin 只能确认自己地市的分析结果。"""
    analysis = (await db.execute(
        select(AcceptanceReportAnalysis).where(
            AcceptanceReportAnalysis.contract_no == contract_no
        )
    )).scalars().first()
    if not analysis:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "分析结果不存在")

    # city_admin 只能操作自己地市的分析结果
    project = await db.get(Project, contract_no)
    if not admin.check_city(project.city if project else None):
        raise PERMISSION_DENIED

    analysis.verified = True
    analysis.verified_by = body.verified_by or admin.username
    analysis.verified_at = datetime.now(timezone.utc)
    await db.commit()
    return success({"contract_no": contract_no, "verified": True})
