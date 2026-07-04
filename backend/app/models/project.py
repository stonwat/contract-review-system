"""项目表：合同编号即项目标识。"""

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Project(Base, TimestampMixin):
    """项目表。contract_no 是主键，同时也是合同编号。"""

    __tablename__ = "projects"

    contract_no: Mapped[str] = mapped_column(String(100), primary_key=True)
    project_name: Mapped[str | None] = mapped_column(String(200))
    city: Mapped[str | None] = mapped_column(String(20))
    # 材料完整性标记（应用层维护一致性）
    has_front_contract: Mapped[bool] = mapped_column(Boolean, default=False)
    has_back_contract: Mapped[bool] = mapped_column(Boolean, default=False)
    has_front_acceptance: Mapped[bool] = mapped_column(Boolean, default=False)
    has_back_acceptance: Mapped[bool] = mapped_column(Boolean, default=False)
    # LLM 分析状态
    llm_analyzed: Mapped[bool] = mapped_column(Boolean, default=False)
    project_risk: Mapped[str | None] = mapped_column(String(10))
    # 人工审查
    responsible_person: Mapped[str | None] = mapped_column(String(50))
    audit_status: Mapped[str] = mapped_column(String(20), default="待审查")
    audited_by: Mapped[str | None] = mapped_column(String(50))
    audited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "project_risk IN ('低风险', '高风险')", name="ck_projects_project_risk"
        ),
        CheckConstraint(
            "audit_status IN ('待审查', '已完成')", name="ck_projects_audit_status"
        ),
    )

