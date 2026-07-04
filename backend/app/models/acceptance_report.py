"""验收报告表。"""

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKey


class AcceptanceReport(Base, UUIDPrimaryKey, TimestampMixin):
    """验收报告。通过 contract_no + acceptance_type 隐式匹配对应合同，不建直接 FK。"""

    __tablename__ = "acceptance_reports"

    acceptance_no: Mapped[str | None] = mapped_column(String(100))
    contract_no: Mapped[str] = mapped_column(
        String(100), ForeignKey("projects.contract_no")
    )
    acceptance_type: Mapped[str | None] = mapped_column(String(10))
    type_judge_basis: Mapped[str | None] = mapped_column(String(200))

    acceptance_content: Mapped[str | None] = mapped_column(Text)
    acceptance_date: Mapped[date | None] = mapped_column(Date)
    acceptance_result: Mapped[str | None] = mapped_column(String(20))

    # 文件溯源
    source_file_name: Mapped[str | None] = mapped_column(String(300))

    # 状态
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_by: Mapped[str | None] = mapped_column(String(50))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    extracted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint(
            "contract_no", "acceptance_type", name="uq_acceptance_no_type"
        ),
        CheckConstraint(
            "acceptance_type IN ('前项', '后项')", name="ck_acceptance_type"
        ),
        CheckConstraint(
            "acceptance_result IN ('通过', '不通过', '附条件通过')",
            name="ck_acceptance_result",
        ),
        Index("idx_acceptance_contract_no", "contract_no"),
    )
