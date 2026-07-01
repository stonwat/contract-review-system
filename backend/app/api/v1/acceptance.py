"""验收报告路由。"""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AgentAuth, CurrentAdmin
from app.db.database import get_db
from app.models.acceptance_report import AcceptanceReport
from app.schemas.acceptance import AcceptanceCreate, AcceptanceUpdate
from app.schemas.common import success

router = APIRouter(prefix="/acceptance", tags=["验收报告"])


@router.post("")
async def create_acceptance(
    body: AcceptanceCreate,
    db: AsyncSession = Depends(get_db),
    _: AgentAuth = None,
) -> dict:
    """Agent 推送验收报告提取结果。"""
    report = AcceptanceReport(
        acceptance_no=body.acceptance_no,
        contract_id=body.contract_id,
        contract_no=body.contract_no,
        acceptance_type=body.acceptance_type,
        type_judge_basis=body.type_judge_basis,
        acceptance_content=body.acceptance_content,
        acceptance_date=body.acceptance_date,
        acceptance_result=body.acceptance_result,
        source_file_name=body.source_file_name,
        source_file_hash=body.source_file_hash,
        ocr_raw_text=body.ocr_raw_text,
        ocr_engine=body.ocr_engine,
        llm_model=body.llm_model,
        extracted_at=datetime.now(timezone.utc),
    )
    db.add(report)
    await db.commit()
    return success({"acceptance_id": str(report.id)})


@router.get("/{report_id}")
async def get_acceptance(
    report_id: UUID, db: AsyncSession = Depends(get_db)
) -> dict:
    """验收详情。"""
    report = await db.get(AcceptanceReport, report_id)
    if not report:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "验收报告不存在")
    return success({"id": str(report.id)})


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
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(report, field, value)
    await db.commit()
    return success({"id": str(report.id)})


@router.post("/{report_id}/verify")
async def verify_acceptance(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """人工确认验收报告。"""
    report = await db.get(AcceptanceReport, report_id)
    if not report:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "验收报告不存在")
    report.verified = True
    report.verified_by = admin.username
    report.verified_at = datetime.now(timezone.utc)
    await db.commit()
    return success({"id": str(report.id), "verified": True})
