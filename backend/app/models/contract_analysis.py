"""前后项合同对比分析表。每个项目一条记录，覆盖式更新。"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKey


class ContractAnalysis(Base, UUIDPrimaryKey, TimestampMixin):
    """LLM 前后项合同对比分析结果。1:1 关联 projects，覆盖式 UPDATE。"""

    __tablename__ = "contract_analysis"

    contract_no: Mapped[str] = mapped_column(
        String(100), ForeignKey("projects.contract_no")
    )
    rate: Mapped[float | None] = mapped_column(Numeric(6, 4))  # 毛利率
    rate_level: Mapped[str | None] = mapped_column(String(20))  # 正常/低毛利/利润倒挂
    similarity: Mapped[str | None] = mapped_column(String(20))  # 完全一致/有一致性风险/完全不一致
    analysis: Mapped[str | None] = mapped_column(Text)  # LLM 分析文本

    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_by: Mapped[str | None] = mapped_column(String(50))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("contract_no", name="uq_contract_analysis_no"),
        CheckConstraint(
            "rate_level IN ('正常', '低毛利', '利润倒挂')",
            name="ck_ca_rate_level",
        ),
        CheckConstraint(
            "similarity IN ('完全一致', '有一致性风险', '完全不一致')",
            name="ck_ca_similarity",
        ),
        Index("idx_contract_analysis_no", "contract_no"),
    )
