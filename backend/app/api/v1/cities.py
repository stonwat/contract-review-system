"""地市枚举接口。"""

from fastapi import APIRouter, Depends

from app.core.auth import CurrentAdmin
from app.schemas.common import success

router = APIRouter(prefix="/cities", tags=["地市"])

CITIES = [
    "哈尔滨", "齐齐哈尔", "牡丹江", "佳木斯", "大庆",
    "鸡西", "双鸭山", "伊春", "七台河", "鹤岗",
    "黑河", "绥化", "大兴安岭",
]


@router.get("")
async def list_cities(admin: CurrentAdmin = None) -> dict:
    """获取黑龙江省地市列表。登录用户可调用，用于前端下拉框选项。"""
    return success(CITIES)
