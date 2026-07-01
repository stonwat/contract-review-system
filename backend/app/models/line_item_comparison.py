"""分项比对表。"""

from uuid import UUID

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKey


class LineItemComparison(Base, UUIDPrimaryKey):
    """前项和后项合同之间逐条分项的匹配和比对结果。"""

    __tablename__ = "line_item_comparisons"

    comparison_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("comparisons.id", ondelete="CASCADE"),
    )
    front_item_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("line_items.id")
    )
    back_item_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("line_items.id")
    )
    item_name: Mapped[str | None] = mapped_column(String(300))

    front_quantity: Mapped[float | None] = mapped_column(Numeric(14, 4))
    back_quantity: Mapped[float | None] = mapped_column(Numeric(14, 4))
    quantity_diff: Mapped[float | None] = mapped_column(Numeric(14, 4))

    front_unit_price: Mapped[float | None] = mapped_column(Numeric(14, 4))
    back_unit_price: Mapped[float | None] = mapped_column(Numeric(14, 4))
    price_diff: Mapped[float | None] = mapped_column(Numeric(14, 4))

    front_amount: Mapped[float | None] = mapped_column(Numeric(14, 2))
    back_amount: Mapped[float | None] = mapped_column(Numeric(14, 2))
    amount_diff: Mapped[float | None] = mapped_column(Numeric(14, 2))

    margin_rate: Mapped[float | None] = mapped_column(Numeric(6, 4))
    risk_level: Mapped[str | None] = mapped_column(String(10))
    risk_reason: Mapped[str | None] = mapped_column(Text)
    match_status: Mapped[str | None] = mapped_column(String(20))
