"""models 包初始化，集中导入所有模型，便于自动检测。"""

from app.models.acceptance_report import AcceptanceReport
from app.models.acceptance_report_analysis import AcceptanceReportAnalysis
from app.models.admin import Admin
from app.models.contract import Contract
from app.models.contract_analysis import ContractAnalysis
from app.models.project import Project
from app.models.base import Base, TimestampMixin, UUIDPrimaryKey

__all__ = [
    "Base",
    "UUIDPrimaryKey",
    "TimestampMixin",
    "Project",
    "Contract",
    "AcceptanceReport",
    "ContractAnalysis",
    "AcceptanceReportAnalysis",
    "Admin",
]
