"""验收报告相关 schema。"""

from datetime import date
from uuid import UUID

from pydantic import BaseModel


class AcceptanceCreate(BaseModel):
    """Agent 推送验收报告提取结果。"""

    acceptance_no: str | None = None
    contract_id: UUID | None = None
    contract_no: str
    acceptance_type: str | None = None
    type_judge_basis: str | None = None
    acceptance_content: str | None = None
    acceptance_date: date | None = None
    acceptance_result: str | None = None
    source_file_name: str | None = None
    source_file_hash: str | None = None
    ocr_raw_text: str | None = None
    ocr_engine: str | None = None
    llm_model: str | None = None


class AcceptanceUpdate(BaseModel):
    acceptance_content: str | None = None
    acceptance_date: date | None = None
    acceptance_result: str | None = None


class AcceptanceOut(AcceptanceCreate):
    id: UUID
    verified: bool = False
    verified_by: str | None = None
    comparison_result: str | None = None
    content_diff_detail: str | None = None
    date_logic: str | None = None

    model_config = {"from_attributes": True}
