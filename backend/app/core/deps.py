"""通用依赖：分页参数等。"""

from dataclasses import dataclass

from fastapi import Query


@dataclass
class PaginationParams:
    """分页参数。page 从 1 开始，page_size 默认 20，上限 100。"""

    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def get_pagination(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginationParams:
    """FastAPI 依赖：解析分页参数。"""
    return PaginationParams(page=page, page_size=page_size)


PaginationDep = PaginationParams
