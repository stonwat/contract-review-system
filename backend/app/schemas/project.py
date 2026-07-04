"""项目相关 schema。"""

from datetime import datetime

from pydantic import BaseModel


class ProjectOut(BaseModel):
    """项目详情。"""

    contract_no: str
    project_name: str | None = None
    city: str | None = None
    has_front_contract: bool = False
    has_back_contract: bool = False
    has_front_acceptance: bool = False
    has_back_acceptance: bool = False
    llm_analyzed: bool = False
    project_risk: str | None = None
    responsible_person: str | None = None
    audit_status: str = "待审查"
    audited_by: str | None = None
    audited_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ProjectUpdate(BaseModel):
    """人工修正项目字段。所有字段可选。"""

    project_name: str | None = None
    city: str | None = None
    responsible_person: str | None = None
    audit_status: str | None = None  # 待审查/已完成
    project_risk: str | None = None  # 低风险/高风险
    llm_analyzed: bool | None = None
