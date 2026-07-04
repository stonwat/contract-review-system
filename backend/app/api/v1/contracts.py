"""合同路由：Agent 推送、列表、详情、修正、确认、删除、去重检查。"""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AgentAuth, CurrentAdmin, PERMISSION_DENIED
from app.core.deps import PaginationParams, get_pagination
from app.db.database import get_db
from app.models.contract import Contract
from app.models.project import Project
from app.schemas.common import success
from app.schemas.contract import (
    ContractCreate,
    ContractDetail,
    ContractListItem,
    ContractUpdate,
    ProjectCardItem,
    VerifyRequest,
)

router = APIRouter(prefix="/contracts", tags=["合同管理"])


# ── 工具函数 ──────────────────────────────────────────────


def _update_has_flag(project: Project, contract_type: str, value: bool) -> None:
    """根据合同类型更新 projects 表对应的 has_* 布尔标记。"""
    if contract_type == "前项":
        project.has_front_contract = value
    elif contract_type == "后项":
        project.has_back_contract = value


async def _get_project_city(contract_no: str, db: AsyncSession) -> str | None:
    """通过 contract_no 获取项目地市。"""
    project = await db.get(Project, contract_no)
    return project.city if project else None


# ── 去重检查 ──────────────────────────────────────────────


@router.get("/check")
async def check_duplicate(
    contract_no: str = Query(..., description="合同编号"),
    contract_type: str = Query(..., description="合同类型：前项/后项"),
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """Agent 插入前去重检查：同编号同类型是否已存在。"""
    existing = (await db.execute(
        select(Contract).where(
            Contract.contract_no == contract_no,
            Contract.contract_type == contract_type,
        )
    )).scalars().first()

    return success({
        "exists": existing is not None,
        "contract_id": str(existing.id) if existing else None,
    })


# ── 按项目分组的卡片列表 ──────────────────────────────────


@router.get("/cards")
async def list_project_cards(
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
    city: str | None = Query(None),
    verified: bool | None = Query(None),
    keyword: str | None = Query(None),
) -> dict:
    """按项目分组返回前后项合同卡片数据。"""
    # 查找所有项目
    project_stmt = select(Project)
    if city:
        project_stmt = project_stmt.where(Project.city == city)
    if keyword:
        project_stmt = project_stmt.where(
            Project.contract_no.ilike(f"%{keyword}%")
            | Project.project_name.ilike(f"%{keyword}%")
        )
    projects = (await db.execute(project_stmt)).scalars().all()

    cards = []
    for p in projects:
        # 查找该项目的前后项合同
        contracts_result = (await db.execute(
            select(Contract).where(Contract.contract_no == p.contract_no)
        )).scalars().all()

        front_contract = None
        back_contract = None
        for c in contracts_result:
            if verified is not None and c.verified != verified:
                continue
            if c.contract_type == "前项":
                front_contract = c
            elif c.contract_type == "后项":
                back_contract = c

        card = ProjectCardItem(
            contract_no=p.contract_no,
            project_name=p.project_name,
            city=p.city,
            has_front_contract=p.has_front_contract,
            has_back_contract=p.has_back_contract,
            has_front_acceptance=p.has_front_acceptance,
            has_back_acceptance=p.has_back_acceptance,
            llm_analyzed=p.llm_analyzed,
            project_risk=p.project_risk,
            audit_status=p.audit_status,
            front_contract=ContractListItem.model_validate(front_contract) if front_contract else None,
            back_contract=ContractListItem.model_validate(back_contract) if back_contract else None,
        )
        cards.append(card.model_dump())

    return success({"items": cards, "total": len(cards)})


# ── 合同 CRUD ──────────────────────────────────────────────


@router.post("")
async def create_contract(
    body: ContractCreate,
    db: AsyncSession = Depends(get_db),
    _: AgentAuth = None,
) -> dict:
    """Agent 推送合同提取结果。自动创建项目（若不存在），并维护 has_* 标记。"""
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
        extracted_at=datetime.now(timezone.utc),
    )
    db.add(contract)

    await db.flush()

    # 3. 维护 projects 表的 has_* 布尔标记
    _update_has_flag(project, body.contract_type, True)

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
    admin: CurrentAdmin = None,
    contract_no: str | None = Query(None),
    contract_type: str | None = Query(None),
    verified: bool | None = Query(None),
) -> dict:
    """合同列表（分页，传统表格式）。"""
    stmt = (
        select(Contract, Project.city, Project.project_name)
        .outerjoin(Project, Contract.contract_no == Project.contract_no)
    )
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
    rows = result.all()

    items = []
    for contract, city, project_name in rows:
        item = ContractListItem.model_validate(contract).model_dump()
        item["city"] = city
        item["project_name"] = project_name
        items.append(item)

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
    contract_id: UUID, db: AsyncSession = Depends(get_db), admin: CurrentAdmin = None
) -> dict:
    """合同详情。"""
    contract = await db.get(Contract, contract_id)
    if not contract:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "合同不存在")

    detail = ContractDetail.model_validate(contract).model_dump()
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

    # city_admin 只能操作自己地市的合同
    city = await _get_project_city(contract.contract_no, db)
    if not admin.check_city(city):
        raise PERMISSION_DENIED

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
    """人工确认合同。city_admin 只能确认自己地市的合同。"""
    contract = await db.get(Contract, contract_id)
    if not contract:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "合同不存在")

    # city_admin 只能操作自己地市的合同
    city = await _get_project_city(contract.contract_no, db)
    if not admin.check_city(city):
        raise PERMISSION_DENIED

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
    """删除合同。仅 super_admin 可删除。删除后回置 projects 表对应的 has_* 标记。"""
    if not admin.is_super_admin:
        raise PERMISSION_DENIED

    contract = await db.get(Contract, contract_id)
    if not contract:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "合同不存在")
    contract_no = contract.contract_no
    contract_type = contract.contract_type
    await db.delete(contract)
    await db.flush()

    # 回置 has_* 标记（仅当该项目无同类型合同剩余时）
    project = await db.get(Project, contract_no)
    if project:
        remaining = (await db.execute(
            select(Contract).where(
                Contract.contract_no == contract_no,
                Contract.contract_type == contract_type,
            )
        )).scalars().all()
        if not remaining:
            _update_has_flag(project, contract_type, False)

    await db.commit()
    return success(message="删除成功")
