"""验收报告相关 schema。"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class AcceptanceCreate(BaseModel):
    """Agent 推送验收报告提取结果。"""

    acceptance_no: str | None = None
    contract_no: str
    acceptance_type: str | None = None
    type_judge_basis: str | None = None
    acceptance_content: str | None = None
    acceptance_date: date | None = None
    acceptance_result: str | None = None
    source_file_name: str | None = None


class AcceptanceUpdate(BaseModel):
    acceptance_content: str | None = None
    acceptance_date: date | None = None
    acceptance_result: str | None = None


class AcceptanceListItem(BaseModel):
    """验收报告列表项。"""
    id: UUID
    acceptance_no: str | None = None
    contract_no: str
    acceptance_type: str | None = None
    acceptance_date: date | None = None
    acceptance_result: str | None = None
    verified: bool = False
    source_file_name: str | None = None

    model_config = {"from_attributes": True}


class AcceptanceOut(BaseModel):
    """验收报告详情。"""
    id: UUID
    acceptance_no: str | None = None
    contract_no: str
    acceptance_type: str | None = None
    type_judge_basis: str | None = None
    acceptance_content: str | None = None
    acceptance_date: date | None = None
    acceptance_result: str | None = None
    source_file_name: str | None = None
    verified: bool = False
    verified_by: str | None = None
    verified_at: datetime | None = None

    model_config = {"from_attributes": True}
