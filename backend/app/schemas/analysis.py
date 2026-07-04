"""分析结果相关 schema。"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ContractAnalysisCreate(BaseModel):
    """Agent 推送合同对比分析结果（UPSERT）。"""

    contract_no: str
    rate: float | None = None
    rate_level: str | None = None  # 正常/低毛利/利润倒挂
    similarity: str | None = None  # 完全一致/有一致性风险/完全不一致
    analysis: str | None = None


class ContractAnalysisOut(BaseModel):
    """合同分析结果。"""

    id: UUID
    contract_no: str
    rate: float | None = None
    rate_level: str | None = None
    similarity: str | None = None
    analysis: str | None = None
    verified: bool = False
    verified_by: str | None = None
    verified_at: datetime | None = None

    model_config = {"from_attributes": True}


class AcceptanceAnalysisCreate(BaseModel):
    """Agent 推送验收报告对比分析结果（UPSERT）。"""

    contract_no: str
    similarity: str | None = None  # 完全一致/有一致性风险/完全不一致
    analysis: str | None = None


class AcceptanceAnalysisOut(BaseModel):
    """验收报告分析结果。"""

    id: UUID
    contract_no: str
    similarity: str | None = None
    analysis: str | None = None
    verified: bool = False
    verified_by: str | None = None
    verified_at: datetime | None = None

    model_config = {"from_attributes": True}


class VerifyAnalysisRequest(BaseModel):
    """人工确认分析结果。"""

    verified_by: str | None = None
