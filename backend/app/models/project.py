"""项目表：合同编号即项目标识。"""

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Project(Base, TimestampMixin):
    """项目表。contract_no 是主键，同时也是合同编号。"""

    __tablename__ = "projects"

    contract_no: Mapped[str] = mapped_column(String(100), primary_key=True)
    project_name: Mapped[str | None] = mapped_column(String(200))
    city: Mapped[str | None] = mapped_column(String(20))
    responsible_person: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="待审查")
    risk_level: Mapped[str | None] = mapped_column(String(10))
