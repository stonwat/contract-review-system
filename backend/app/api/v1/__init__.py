"""API v1 路由聚合。"""

from fastapi import APIRouter

from app.api.v1 import (
    acceptance,
    acceptance_analysis,
    admins,
    auth,
    cities,
    contract_analysis,
    contracts,
    dashboard,
    files,
    projects,
    reports,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(contracts.router)
api_router.include_router(acceptance.router)
api_router.include_router(projects.router)
api_router.include_router(contract_analysis.router)
api_router.include_router(acceptance_analysis.router)
api_router.include_router(reports.router)
api_router.include_router(dashboard.router)
api_router.include_router(files.router)
api_router.include_router(admins.router)
api_router.include_router(cities.router)
