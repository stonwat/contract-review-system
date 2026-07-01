"""原始文件表。"""

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKey


class SourceFile(Base, UUIDPrimaryKey):
    """上传文件的元数据。文件内容存 MinIO。"""

    __tablename__ = "source_files"

    file_name: Mapped[str | None] = mapped_column(String(300))
    file_type: Mapped[str | None] = mapped_column(String(20))
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    file_hash: Mapped[str | None] = mapped_column(String(64), unique=True)
    storage_path: Mapped[str | None] = mapped_column(String(500))
    upload_by: Mapped[str | None] = mapped_column(String(50))
