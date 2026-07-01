"""异步任务：OCR 处理。骨架，实际通过 arq 投递执行。"""

from app.db.database import async_session_factory


async def run_ocr_task(file_id: str) -> None:
    """OCR 提取任务。骨架。"""
    # 实际实现：
    # 1. 从 MinIO 下载文件
    # 2. 调用 PaddleOCR 识别
    # 3. 调用 LLM 提取字段
    # 4. 写入数据库
    _ = await async_session_factory()
