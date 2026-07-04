"""文件上传路由。"""

import io

from fastapi import APIRouter, Depends, UploadFile
from minio import Minio

import hashlib

from app.config import settings
from app.core.auth import CurrentAdmin
from app.schemas.common import success

router = APIRouter(prefix="/files", tags=["文件管理"])

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_TYPES = {"pdf", "docx", "xls", "xlsx", "jpg", "png"}


def _get_minio_client() -> Minio:
    """创建 MinIO 客户端。"""
    return Minio(
        endpoint=settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


def _ensure_bucket(client: Minio) -> None:
    """确保存储桶存在。"""
    bucket = settings.minio_bucket
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)


@router.post("/upload")
async def upload_files(
    files: list[UploadFile],
    _: CurrentAdmin = None,
) -> dict:
    """上传原始文件（支持批量），存储到 MinIO，返回 object_key。"""
    client = _get_minio_client()
    _ensure_bucket(client)

    results = []
    for f in files:
        content = await f.read()
        if len(content) > MAX_FILE_SIZE:
            continue
        file_hash = hashlib.sha256(content).hexdigest()
        ext = (f.filename or "").rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED_TYPES:
            continue

        # 存储到 MinIO：路径为 {hash前2位}/{hash}.{ext}
        object_name = f"{file_hash[:2]}/{file_hash}.{ext}"
        client.put_object(
            bucket_name=settings.minio_bucket,
            object_name=object_name,
            data=io.BytesIO(content),
            length=len(content),
            content_type=f.content_type or "application/octet-stream",
        )

        results.append(
            {
                "object_key": object_name,
                "file_name": f.filename,
                "file_size": len(content),
                "file_hash": file_hash,
            }
        )
    return success(results)
