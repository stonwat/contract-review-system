"""验收报告表。"""

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKey


class AcceptanceReport(Base, UUIDPrimaryKey, TimestampMixin):
    """验收报告。"""

    __tablename__ = "acceptance_reports"

    acceptance_no: Mapped[str | None] = mapped_column(String(100))
    contract_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("contracts.id")
    )
    contract_no: Mapped[str] = mapped_column(
        String(100), ForeignKey("projects.contract_no")
    )
    acceptance_type: Mapped[str | None] = mapped_column(String(10))
    type_judge_basis: Mapped[str | None] = mapped_column(String(200))

    acceptance_content: Mapped[str | None] = mapped_column(Text)
    acceptance_date: Mapped[date | None] = mapped_column(Date)
    acceptance_result: Mapped[str | None] = mapped_column(String(20))

    # 验收比对
    pair_report_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("acceptance_reports.id")
    )
    comparison_result: Mapped[str | None] = mapped_column(String(10))
    content_diff_detail: Mapped[str | None] = mapped_column(Text)
    date_logic: Mapped[str | None] = mapped_column(String(10))

    # 文件溯源
    source_file_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    source_file_name: Mapped[str | None] = mapped_column(String(300))
    source_file_hash: Mapped[str | None] = mapped_column(String(64))
    ocr_raw_text: Mapped[str | None] = mapped_column(Text)
    ocr_engine: Mapped[str | None] = mapped_column(String(20))
    llm_model: Mapped[str | None] = mapped_column(String(50))

    # 状态
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_by: Mapped[str | None] = mapped_column(String(50))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    extracted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
