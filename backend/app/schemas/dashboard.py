"""仪表盘相关 schema。"""

from pydantic import BaseModel


class DashboardOverview(BaseModel):
    project_count: int
    contract_count: int
    pending_verify_count: int
    high_risk_count: int
    completed_count: int
    llm_analyzed_count: int = 0
    front_count: int = 0
    back_count: int = 0
    ready_count: int = 0


class CityStat(BaseModel):
    city: str
    project_count: int
    high_risk: int
    pending_verify: int
    completed: int
