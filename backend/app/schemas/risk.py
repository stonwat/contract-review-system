"""风险相关 schema。"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RiskListItem(BaseModel):
    id: UUID
    contract_no: str
    risk_type: str
    risk_level: str
    source_type: str
    detail: str | None = None
    dismissed: bool = False
    dismissed_by: str | None = None
    dismissed_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DismissRequest(BaseModel):
    dismissed_by: str | None = None


class RiskSummary(BaseModel):
    total: int
    by_level: dict[str, int]
    by_city: list[dict]
