"""合同路由：Agent 推送、列表、详情、修正、确认、删除。"""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AgentAuth, CurrentAdmin
from app.core.deps import PaginationParams, get_pagination
from app.db.database import get_db
from app.models.contract import Contract
from app.models.line_item import LineItem
from app.models.project import Project
from app.schemas.common import success
from app.schemas.contract import (
    ContractCreate,
    ContractDetail,
    ContractListItem,
    ContractUpdate,
    LineItemCreate,
    LineItemOut,
    VerifyRequest,
)

router = APIRouter(prefix="/contracts", tags=["合同管理"])


@router.post("")
async def create_contract(
    body: ContractCreate,
    db: AsyncSession = Depends(get_db),
    _: AgentAuth = None,
) -> dict:
    """Agent 推送合同提取结果。自动创建项目（若不存在）。"""
    # 1. 确保项目存在
    project = await db.get(Project, body.contract_no)
    project_created = False
    if not project:
        project = Project(contract_no=body.contract_no)
        db.add(project)
        await db.flush()
        project_created = True

    # 2. 创建合同
    contract = Contract(
        contract_no=body.contract_no,
        contract_type=body.contract_type,
        type_judge_basis=body.type_judge_basis,
        party_a=body.party_a,
        party_b=body.party_b,
        our_role=body.our_role,
        signing_date=body.signing_date,
        contract_period=body.contract_period,
        total_amount=body.total_amount,
        amount_uppercase=body.amount_uppercase,
        tax_rate=body.tax_rate,
        payment_terms=body.payment_terms,
        delivery_terms=body.delivery_terms,
        acceptance_terms=body.acceptance_terms,
        breach_terms=body.breach_terms,
        warranty_terms=body.warranty_terms,
        ip_terms=body.ip_terms,
        other_key_terms=body.other_key_terms,
        source_file_name=body.source_file_name,
        source_file_hash=body.source_file_hash,
        ocr_raw_text=body.ocr_raw_text,
        ocr_engine=body.ocr_engine,
        llm_model=body.llm_model,
        extracted_at=datetime.now(timezone.utc),
    )
    db.add(contract)

    # 3. 创建分项清单
    for item in body.line_items:
        db.add(LineItem(contract_id=contract.id, **item.model_dump()))

    await db.commit()
    return success(
        {
            "contract_id": str(contract.id),
            "contract_no": body.contract_no,
            "project_created": project_created,
        }
    )


@router.get("")
async def list_contracts(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination),
    contract_no: str | None = Query(None),
    contract_type: str | None = Query(None),
    verified: bool | None = Query(None),
) -> dict:
    """合同列表（分页）。"""
    stmt = select(Contract)
    count_stmt = select(func.count(Contract.id))

    if contract_no:
        stmt = stmt.where(Contract.contract_no.ilike(f"%{contract_no}%"))
        count_stmt = count_stmt.where(Contract.contract_no.ilike(f"%{contract_no}%"))
    if contract_type:
        stmt = stmt.where(Contract.contract_type == contract_type)
        count_stmt = count_stmt.where(Contract.contract_type == contract_type)
    if verified is not None:
        stmt = stmt.where(Contract.verified == verified)
        count_stmt = count_stmt.where(Contract.verified == verified)

    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(
        stmt.order_by(Contract.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    )
    contracts = result.scalars().all()

    items = [ContractListItem.model_validate(c).model_dump() for c in contracts]
    return success(
        {
            "items": items,
            "total": total,
            "page": pagination.page,
            "page_size": pagination.page_size,
        }
    )


@router.get("/{contract_id}")
async def get_contract(
    contract_id: UUID, db: AsyncSession = Depends(get_db)
) -> dict:
    """合同详情（含分项清单）。"""
    contract = await db.get(Contract, contract_id)
    if not contract:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "合同不存在")

    items_result = await db.execute(
        select(LineItem)
        .where(LineItem.contract_id == contract_id)
        .order_by(LineItem.sort_order, LineItem.item_no)
    )
    line_items = items_result.scalars().all()

    detail = ContractDetail.model_validate(contract).model_dump()
    detail["line_items"] = [LineItemOut.model_validate(i).model_dump() for i in line_items]
    return success(detail)


@router.put("/{contract_id}")
async def update_contract(
    contract_id: UUID,
    body: ContractUpdate,
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """修正合同字段。"""
    contract = await db.get(Contract, contract_id)
    if not contract:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "合同不存在")
    if contract.verified:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "已确认的合同需先取消确认")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(contract, field, value)
    await db.commit()
    return success({"id": str(contract.id), "updated_at": str(contract.updated_at)})


@router.post("/{contract_id}/verify")
async def verify_contract(
    contract_id: UUID,
    body: VerifyRequest,
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """人工确认合同。"""
    contract = await db.get(Contract, contract_id)
    if not contract:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "合同不存在")

    contract.verified = True
    contract.verified_by = body.verified_by or admin.username
    contract.verified_at = datetime.now(timezone.utc)
    await db.commit()
    return success(
        {
            "id": str(contract.id),
            "verified": True,
            "verified_at": str(contract.verified_at),
        }
    )


@router.delete("/{contract_id}")
async def delete_contract(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """删除合同。"""
    contract = await db.get(Contract, contract_id)
    if not contract:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "合同不存在")
    await db.delete(contract)
    await db.commit()
    return success(message="删除成功")
