"""API v1 路由聚合。"""

from fastapi import APIRouter

from app.api.v1 import acceptance, auth, comparisons, contracts, dashboard, files, reports, risks

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(contracts.router)
api_router.include_router(comparisons.router)
api_router.include_router(acceptance.router)
api_router.include_router(risks.router)
api_router.include_router(reports.router)
api_router.include_router(dashboard.router)
api_router.include_router(files.router)
