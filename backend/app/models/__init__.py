"""models 包初始化，集中导入所有模型，便于 Alembic 自动检测。"""

from app.models.base import Base, TimestampMixin, UUIDPrimaryKey
from app.models.acceptance_report import AcceptanceReport
from app.models.admin import Admin
from app.models.audit_log import AuditLog
from app.models.comparison import Comparison
from app.models.contract import Contract
from app.models.line_item import LineItem
from app.models.line_item_comparison import LineItemComparison
from app.models.project import Project
from app.models.risk_record import RiskRecord
from app.models.source_file import SourceFile

__all__ = [
    "Base",
    "UUIDPrimaryKey",
    "TimestampMixin",
    "Project",
    "Contract",
    "LineItem",
    "Comparison",
    "LineItemComparison",
    "AcceptanceReport",
    "RiskRecord",
    "SourceFile",
    "AuditLog",
    "Admin",
]
