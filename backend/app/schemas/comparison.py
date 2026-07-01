"""比对相关 schema。"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ComparisonCreate(BaseModel):
    front_contract_id: UUID
    back_contract_id: UUID


class ComparisonListItem(BaseModel):
    id: UUID
    contract_no: str
    city: str | None = None
    front_amount: float | None = None
    back_amount: float | None = None
    amount_diff: float | None = None
    margin_rate: float | None = None
    amount_match: str | None = None
    payment_match: str | None = None
    delivery_match: str | None = None
    acceptance_match: str | None = None
    other_match: str | None = None
    compared_at: datetime | None = None

    model_config = {"from_attributes": True}


class LineItemComparisonOut(BaseModel):
    id: UUID
    item_name: str | None = None
    front_quantity: float | None = None
    back_quantity: float | None = None
    quantity_diff: float | None = None
    front_unit_price: float | None = None
    back_unit_price: float | None = None
    price_diff: float | None = None
    match_status: str | None = None
    risk_level: str | None = None
    risk_reason: str | None = None

    model_config = {"from_attributes": True}


class ComparisonDetail(ComparisonListItem):
    payment_diff_detail: str | None = None
    delivery_diff_detail: str | None = None
    acceptance_diff_detail: str | None = None
    other_diff_detail: str | None = None
    llm_model: str | None = None
    line_items: list[LineItemComparisonOut] = []
