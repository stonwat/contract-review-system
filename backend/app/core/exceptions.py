"""统一异常处理。"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class BusinessError(Exception):
    """业务错误，返回非 0 的业务错误码。"""

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器。"""

    @app.exception_handler(BusinessError)
    async def business_error_handler(request: Request, exc: BusinessError) -> JSONResponse:
        return JSONResponse(
            status_code=200,
            content={"code": exc.code, "message": exc.message, "data": None},
        )
