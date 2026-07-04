"""合同对比分析路由：Agent UPSERT、查询、人工确认。"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AgentAuth, CurrentAdmin, PERMISSION_DENIED
from app.db.database import get_db
from app.models.contract_analysis import ContractAnalysis
from app.models.project import Project
from app.schemas.analysis import ContractAnalysisCreate, ContractAnalysisOut, VerifyAnalysisRequest
from app.schemas.common import success

router = APIRouter(prefix="/contract-analysis", tags=["合同分析"])


@router.post("")
async def upsert_contract_analysis(
    body: ContractAnalysisCreate,
    db: AsyncSession = Depends(get_db),
    _: AgentAuth = None,
) -> dict:
    """Agent 推送合同对比分析结果。UPSERT：存在则更新，不存在则创建。"""
    existing = (await db.execute(
        select(ContractAnalysis).where(
            ContractAnalysis.contract_no == body.contract_no
        )
    )).scalars().first()

    if existing:
        existing.rate = body.rate
        existing.rate_level = body.rate_level
        existing.similarity = body.similarity
        existing.analysis = body.analysis
        analysis = existing
    else:
        analysis = ContractAnalysis(
            contract_no=body.contract_no,
            rate=body.rate,
            rate_level=body.rate_level,
            similarity=body.similarity,
            analysis=body.analysis,
        )
        db.add(analysis)

    await db.commit()
    return success({"id": str(analysis.id), "contract_no": body.contract_no})


@router.get("/{contract_no}")
async def get_contract_analysis(
    contract_no: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """查询单个项目的合同分析结果。"""
    analysis = (await db.execute(
        select(ContractAnalysis).where(
            ContractAnalysis.contract_no == contract_no
        )
    )).scalars().first()
    if not analysis:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "分析结果不存在")
    return success(ContractAnalysisOut.model_validate(analysis).model_dump())


@router.get("")
async def list_contract_analysis(
    db: AsyncSession = Depends(get_db),
    verified: bool | None = Query(None),
) -> dict:
    """合同分析结果列表。"""
    stmt = select(ContractAnalysis)
    if verified is not None:
        stmt = stmt.where(ContractAnalysis.verified == verified)
    rows = (await db.execute(stmt.order_by(ContractAnalysis.created_at.desc()))).scalars().all()
    items = [ContractAnalysisOut.model_validate(r).model_dump() for r in rows]
    return success({"items": items, "total": len(items)})


@router.post("/{contract_no}/verify")
async def verify_contract_analysis(
    contract_no: str,
    body: VerifyAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """人工确认合同分析结果。city_admin 只能确认自己地市的分析结果。"""
    analysis = (await db.execute(
        select(ContractAnalysis).where(
            ContractAnalysis.contract_no == contract_no
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
