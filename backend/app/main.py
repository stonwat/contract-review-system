"""FastAPI 应用入口。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.config import settings
from app.core.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动与关闭。"""
    # 启动时可做初始化（如 MinIO bucket 检查）
    yield
    # 关闭时清理资源


app = FastAPI(
    title="合同审查系统",
    description="政企工程项目合同风控系统 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 异常处理
register_exception_handlers(app)

# 路由
app.include_router(api_router)


@app.get("/health", tags=["健康检查"])
async def health() -> dict:
    """健康检查。"""
    return {"code": 0, "message": "success", "data": {"status": "ok"}}
