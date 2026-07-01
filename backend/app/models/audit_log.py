"""操作审计表。"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKey


class AuditLog(Base, UUIDPrimaryKey):
    """所有写操作的审计记录。"""

    __tablename__ = "audit_log"

    user_id: Mapped[str | None] = mapped_column(String(50))
    action: Mapped[str | None] = mapped_column(String(50))
    target_type: Mapped[str | None] = mapped_column(String(30))
    target_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    detail: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
