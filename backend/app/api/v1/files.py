"""文件上传路由。"""

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

import hashlib

from app.core.auth import CurrentAdmin
from app.db.database import get_db
from app.models.source_file import SourceFile
from app.schemas.common import success

router = APIRouter(prefix="/files", tags=["文件管理"])

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_TYPES = {"pdf", "docx", "xls", "xlsx", "jpg", "png"}


@router.post("/upload")
async def upload_files(
    files: list[UploadFile],
    db: AsyncSession = Depends(get_db),
    admin: CurrentAdmin = None,
) -> dict:
    """上传原始文件（支持批量），返回 file_id。"""
    results = []
    for f in files:
        content = await f.read()
        if len(content) > MAX_FILE_SIZE:
            continue
        file_hash = hashlib.sha256(content).hexdigest()
        ext = (f.filename or "").rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED_TYPES:
            continue

        source = SourceFile(
            file_name=f.filename,
            file_type=ext,
            file_size=len(content),
            file_hash=file_hash,
            storage_path=f"local/{file_hash}",  # 骨架，实际存 MinIO
            upload_by=admin.username,
        )
        db.add(source)
        results.append(
            {
                "file_id": str(source.id),
                "file_name": f.filename,
                "file_size": len(content),
                "file_hash": file_hash,
            }
        )
    await db.commit()
    return success(results)
