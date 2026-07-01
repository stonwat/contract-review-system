"""通用响应模型。"""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一响应格式。"""

    code: int = 0
    message: str = "success"
    data: T | None = None


class PaginatedData(BaseModel, Generic[T]):
    """分页数据。"""

    items: list[T]
    total: int
    page: int
    page_size: int


def success(data: object = None, message: str = "success") -> dict:
    """构造成功响应。"""
    return {"code": 0, "message": message, "data": data}


def fail(code: int, message: str) -> dict:
    """构造失败响应。"""
    return {"code": code, "message": message, "data": None}
