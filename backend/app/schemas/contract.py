"""合同相关 schema。"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class LineItemCreate(BaseModel):
    item_no: int | None = None
    item_name: str | None = None
    spec: str | None = None
    unit: str | None = None
    quantity: float | None = None
    unit_price: float | None = None
    amount: float | None = None
    remark: str | None = None


class LineItemOut(LineItemCreate):
    id: UUID
    contract_id: UUID

    model_config = {"from_attributes": True}


class ContractCreate(BaseModel):
    """Agent 推送合同提取结果。"""

    contract_no: str
    contract_type: str
    type_judge_basis: str | None = None
    party_a: str | None = None
    party_b: str | None = None
    our_role: str | None = None
    signing_date: date | None = None
    contract_period: str | None = None
    total_amount: float | None = None
    amount_uppercase: str | None = None
    tax_rate: float | None = None
    payment_terms: str | None = None
    delivery_terms: str | None = None
    acceptance_terms: str | None = None
    breach_terms: str | None = None
    warranty_terms: str | None = None
    ip_terms: str | None = None
    other_key_terms: str | None = None
    source_file_name: str | None = None
    source_file_hash: str | None = None
    ocr_raw_text: str | None = None
    ocr_engine: str | None = None
    llm_model: str | None = None
    line_items: list[LineItemCreate] = []


class ContractUpdate(BaseModel):
    """人工修正合同字段。所有字段可选。"""

    party_a: str | None = None
    party_b: str | None = None
    our_role: str | None = None
    signing_date: date | None = None
    contract_period: str | None = None
    total_amount: float | None = None
    amount_uppercase: str | None = None
    tax_rate: float | None = None
    payment_terms: str | None = None
    delivery_terms: str | None = None
    acceptance_terms: str | None = None
    breach_terms: str | None = None
    warranty_terms: str | None = None
    ip_terms: str | None = None
    other_key_terms: str | None = None


class ContractListItem(BaseModel):
    id: UUID
    contract_no: str
    contract_type: str
    party_a: str | None = None
    party_b: str | None = None
    total_amount: float | None = None
    city: str | None = None
    project_name: str | None = None
    verified: bool = False
    verified_by: str | None = None
    verified_at: datetime | None = None

    model_config = {"from_attributes": True}


class ContractDetail(ContractListItem):
    type_judge_basis: str | None = None
    our_role: str | None = None
    signing_date: date | None = None
    contract_period: str | None = None
    amount_uppercase: str | None = None
    tax_rate: float | None = None
    payment_terms: str | None = None
    delivery_terms: str | None = None
    acceptance_terms: str | None = None
    breach_terms: str | None = None
    warranty_terms: str | None = None
    ip_terms: str | None = None
    other_key_terms: str | None = None
    source_file_name: str | None = None
    source_file_hash: str | None = None
    ocr_engine: str | None = None
    llm_model: str | None = None
    extracted_at: datetime | None = None
    line_items: list[LineItemOut] = []


class VerifyRequest(BaseModel):
    verified_by: str | None = None
