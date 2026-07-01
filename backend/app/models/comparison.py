"""合同比对表。"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKey


class Comparison(Base, UUIDPrimaryKey):
    """前后项合同的比对结果。"""

    __tablename__ = "comparisons"

    contract_no: Mapped[str] = mapped_column(
        String(100), ForeignKey("projects.contract_no")
    )
    front_contract_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("contracts.id")
    )
    back_contract_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("contracts.id")
    )

    # 金额比对
    front_amount: Mapped[float | None] = mapped_column(Numeric(14, 2))
    back_amount: Mapped[float | None] = mapped_column(Numeric(14, 2))
    amount_diff: Mapped[float | None] = mapped_column(Numeric(14, 2))
    margin_rate: Mapped[float | None] = mapped_column(Numeric(6, 4))

    # 逐项匹配结果
    amount_match: Mapped[str | None] = mapped_column(String(10))
    payment_match: Mapped[str | None] = mapped_column(String(10))
    delivery_match: Mapped[str | None] = mapped_column(String(10))
    acceptance_match: Mapped[str | None] = mapped_column(String(10))
    other_match: Mapped[str | None] = mapped_column(String(10))

    # 差异详情
    payment_diff_detail: Mapped[str | None] = mapped_column(Text)
    delivery_diff_detail: Mapped[str | None] = mapped_column(Text)
    acceptance_diff_detail: Mapped[str | None] = mapped_column(Text)
    other_diff_detail: Mapped[str | None] = mapped_column(Text)

    # 比对元信息
    llm_model: Mapped[str | None] = mapped_column(String(50))
    compared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
