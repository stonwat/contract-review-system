"""风险记录表。"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKey


class RiskRecord(Base, UUIDPrimaryKey, TimestampMixin):
    """比对引擎自动生成的风险记录。"""

    __tablename__ = "risk_records"

    contract_no: Mapped[str] = mapped_column(
        String(100), ForeignKey("projects.contract_no")
    )
    risk_type: Mapped[str] = mapped_column(String(30))
    risk_level: Mapped[str] = mapped_column(String(10))
    source_type: Mapped[str] = mapped_column(String(30))
    source_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    detail: Mapped[str | None] = mapped_column(Text)

    dismissed: Mapped[bool] = mapped_column(Boolean, default=False)
    dismissed_by: Mapped[str | None] = mapped_column(String(50))
    dismissed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
