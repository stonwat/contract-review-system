"""仪表盘相关 schema。"""

from pydantic import BaseModel


class DashboardOverview(BaseModel):
    project_count: int
    contract_count: int
    pending_verify_count: int
    high_risk_count: int
    completed_count: int


class CityStat(BaseModel):
    city: str
    project_count: int
    high_risk: int
    pending_verify: int
    completed: int
