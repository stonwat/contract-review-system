"""合同表。"""

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
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


class Contract(Base, UUIDPrimaryKey, TimestampMixin):
    """合同表：前项或后项合同记录。"""

    __tablename__ = "contracts"

    contract_no: Mapped[str] = mapped_column(
        String(100), ForeignKey("projects.contract_no")
    )
    contract_type: Mapped[str] = mapped_column(String(10))  # 前项/后项
    type_judge_basis: Mapped[str | None] = mapped_column(String(200))

    # 签约方
    party_a: Mapped[str | None] = mapped_column(String(200))
    party_b: Mapped[str | None] = mapped_column(String(200))
    our_role: Mapped[str | None] = mapped_column(String(10))

    # 合同信息
    signing_date: Mapped[date | None] = mapped_column(Date)
    contract_period: Mapped[str | None] = mapped_column(String(100))

    # 金额
    total_amount: Mapped[float | None] = mapped_column(Numeric(14, 2))
    amount_uppercase: Mapped[str | None] = mapped_column(String(100))
    tax_rate: Mapped[float | None] = mapped_column(Numeric(5, 4))

    # 关键条款
    payment_terms: Mapped[str | None] = mapped_column(Text)
    delivery_terms: Mapped[str | None] = mapped_column(Text)
    acceptance_terms: Mapped[str | None] = mapped_column(Text)
    breach_terms: Mapped[str | None] = mapped_column(Text)
    warranty_terms: Mapped[str | None] = mapped_column(Text)
    ip_terms: Mapped[str | None] = mapped_column(Text)
    other_key_terms: Mapped[str | None] = mapped_column(Text)

    # 文件溯源
    source_file_name: Mapped[str | None] = mapped_column(String(300))

    # 状态
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_by: Mapped[str | None] = mapped_column(String(50))
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    extracted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    __table_args__ = (
        Index("idx_contracts_no", "contract_no"),
        UniqueConstraint(
            "contract_no", "contract_type", name="uq_contracts_no_type"
        ),
        CheckConstraint(
            "contract_type IN ('前项', '后项')", name="ck_contracts_type"
        ),
    )

