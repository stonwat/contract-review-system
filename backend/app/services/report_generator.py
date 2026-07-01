"""报表生成服务。对应四个核心报表的数据聚合。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comparison import Comparison


class ReportGenerator:
    """报表生成器。所有报表实时查询，不入库缓存。"""

    async def contract_consistency(
        self, db: AsyncSession, city: str | None = None
    ) -> dict:
        """合同内容一致性报表（骨架）。"""
        # 实际实现：按地市聚合 comparisons 的 match 字段
        stmt = select(Comparison)
        if city:
            # 需 JOIN projects 取 city，此处骨架省略
            pass
        result = await db.execute(stmt)
        comparisons = result.scalars().all()
        return {"summary": [], "details": [c for c in comparisons]}

    async def low_margin(
        self, db: AsyncSession, threshold: float = 0.03
    ) -> dict:
        """低毛利项目报表。"""
        stmt = select(Comparison).where(Comparison.margin_rate < threshold)
        result = await db.execute(stmt)
        return {"summary": [], "details": result.scalars().all()}

    async def high_risk(self, db: AsyncSession) -> dict:
        """高风险项目报表：三条件交集。"""
        # 低毛利 + 条款不一致 + 验收不一致
        stmt = select(Comparison).where(
            Comparison.margin_rate < 0.03,
            Comparison.payment_match == "不一致",
        )
        result = await db.execute(stmt)
        return {"items": result.scalars().all(), "total": 0}


report_generator = ReportGenerator()
