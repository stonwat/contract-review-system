"""分项工程量清单表。"""

from uuid import UUID

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKey


class LineItem(Base, UUIDPrimaryKey):
    """合同的分项明细条目。"""

    __tablename__ = "line_items"

    contract_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("contracts.id", ondelete="CASCADE"),
    )
    item_no: Mapped[int | None] = mapped_column(Integer)
    item_name: Mapped[str | None] = mapped_column(String(300))
    spec: Mapped[str | None] = mapped_column(String(200))
    unit: Mapped[str | None] = mapped_column(String(20))
    quantity: Mapped[float | None] = mapped_column(Numeric(14, 4))
    unit_price: Mapped[float | None] = mapped_column(Numeric(14, 4))
    amount: Mapped[float | None] = mapped_column(Numeric(14, 2))
    remark: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (Index("idx_line_items_contract", "contract_id"),)
