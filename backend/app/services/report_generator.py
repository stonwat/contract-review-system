"""报表生成服务。基于 LLM 分析结果与项目数据生成报表。"""

from io import BytesIO

from openpyxl import Workbook
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.acceptance_report_analysis import AcceptanceReportAnalysis
from app.models.contract import Contract
from app.models.contract_analysis import ContractAnalysis
from app.models.project import Project


class ReportGenerator:
    """报表生成器。所有报表实时查询，不入库缓存。"""

    async def _load_contracts(self, db: AsyncSession, contract_no: str) -> dict:
        """加载项目前后项合同金额。"""
        rows = (await db.execute(
            select(Contract).where(Contract.contract_no == contract_no)
        )).scalars().all()
        front = next((c for c in rows if c.contract_type == "前项"), None)
        back = next((c for c in rows if c.contract_type == "后项"), None)
        return {
            "front_amount": float(front.total_amount) if front and front.total_amount else None,
            "back_amount": float(back.total_amount) if back and back.total_amount else None,
        }

    async def contract_consistency_report(
        self, db: AsyncSession, city: str | None = None
    ) -> dict:
        """报表一：合同内容一致性。数据源 contract_analysis。"""
        stmt = (
            select(ContractAnalysis, Project.city, Project.project_name)
            .outerjoin(Project, ContractAnalysis.contract_no == Project.contract_no)
        )
        if city:
            stmt = stmt.where(Project.city == city)
        rows = (await db.execute(stmt)).all()

        details = []
        for ca, c, pn in rows:
            amounts = await self._load_contracts(db, ca.contract_no)
            details.append({
                "contract_no": ca.contract_no,
                "project_name": pn,
                "city": c,
                "front_amount": amounts["front_amount"],
                "back_amount": amounts["back_amount"],
                "rate": float(ca.rate) if ca.rate is not None else None,
                "rate_level": ca.rate_level,
                "similarity": ca.similarity,
                "analysis": ca.analysis,
            })

        summary = self._consistency_summary(details)
        return {"summary": summary, "details": details}

    async def acceptance_consistency_report(
        self, db: AsyncSession, city: str | None = None
    ) -> dict:
        """报表二：验收报告一致性。数据源 acceptance_report_analysis。"""
        stmt = (
            select(AcceptanceReportAnalysis, Project.city, Project.project_name)
            .outerjoin(Project, AcceptanceReportAnalysis.contract_no == Project.contract_no)
        )
        if city:
            stmt = stmt.where(Project.city == city)
        rows = (await db.execute(stmt)).all()

        details = []
        for ara, c, pn in rows:
            details.append({
                "contract_no": ara.contract_no,
                "project_name": pn,
                "city": c,
                "similarity": ara.similarity,
                "analysis": ara.analysis,
            })

        summary = self._consistency_summary(details)
        return {"summary": summary, "details": details}

    @staticmethod
    def _consistency_summary(details: list[dict]) -> list[dict]:
        """按地市汇总一致性档位数量。"""
        stats: dict[str, dict] = {}
        for d in details:
            city = d.get("city") or "未知"
            bucket = stats.setdefault(city, {
                "city": city, "完全一致": 0, "有一致性风险": 0, "完全不一致": 0, "total": 0,
            })
            bucket["total"] += 1
            sim = d.get("similarity")
            if sim in bucket:
                bucket[sim] += 1
        return list(stats.values())

    async def low_margin_report(
        self, db: AsyncSession, city: str | None = None
    ) -> dict:
        """报表三：低毛利项目。数据源 contract_analysis.rate_level。"""
        stmt = (
            select(ContractAnalysis, Project.city, Project.project_name)
            .outerjoin(Project, ContractAnalysis.contract_no == Project.contract_no)
            .where(ContractAnalysis.rate_level.in_(["低毛利", "利润倒挂"]))
        )
        if city:
            stmt = stmt.where(Project.city == city)
        rows = (await db.execute(stmt)).all()

        details = []
        for ca, c, pn in rows:
            amounts = await self._load_contracts(db, ca.contract_no)
            details.append({
                "contract_no": ca.contract_no,
                "project_name": pn,
                "city": c,
                "front_amount": amounts["front_amount"],
                "back_amount": amounts["back_amount"],
                "rate": float(ca.rate) if ca.rate is not None else None,
                "rate_level": ca.rate_level,
            })

        # 按地市汇总
        stats: dict[str, dict] = {}
        for d in details:
            city = d.get("city") or "未知"
            bucket = stats.setdefault(city, {"city": city, "low_margin": 0, "inverted": 0})
            if d["rate_level"] == "利润倒挂":
                bucket["inverted"] += 1
            else:
                bucket["low_margin"] += 1
        summary = list(stats.values())

        return {
            "summary": {
                "total": len(details),
                "low_margin": sum(1 for d in details if d["rate_level"] == "低毛利"),
                "inverted": sum(1 for d in details if d["rate_level"] == "利润倒挂"),
                "by_city": summary,
            },
            "details": details,
        }

    async def high_risk_report(
        self, db: AsyncSession, city: str | None = None
    ) -> dict:
        """报表四：高风险项目。数据源 projects.project_risk。"""
        stmt = (
            select(Project).where(Project.project_risk == "高风险")
        )
        if city:
            stmt = stmt.where(Project.city == city)
        projects = (await db.execute(stmt)).scalars().all()

        details = []
        for p in projects:
            # 关联分析结果
            ca = (await db.execute(
                select(ContractAnalysis).where(ContractAnalysis.contract_no == p.contract_no)
            )).scalars().first()
            ara = (await db.execute(
                select(AcceptanceReportAnalysis).where(
                    AcceptanceReportAnalysis.contract_no == p.contract_no
                )
            )).scalars().first()
            amounts = await self._load_contracts(db, p.contract_no)
            details.append({
                "contract_no": p.contract_no,
                "project_name": p.project_name,
                "city": p.city,
                "front_amount": amounts["front_amount"],
                "back_amount": amounts["back_amount"],
                "rate": float(ca.rate) if ca and ca.rate is not None else None,
                "rate_level": ca.rate_level if ca else None,
                "contract_similarity": ca.similarity if ca else None,
                "acceptance_similarity": ara.similarity if ara else None,
                "project_risk": p.project_risk,
            })

        return {"items": details, "total": len(details)}

    async def export_excel(
        self, db: AsyncSession, report_type: str, city: str | None = None
    ) -> BytesIO:
        """生成 Excel 报表。"""
        wb = Workbook()
        ws = wb.active

        if report_type == "contract-consistency":
            data = await self.contract_consistency_report(db, city)
            ws.title = "合同一致性"
            ws.append(["合同编号", "地市", "项目名称", "前项金额", "后项金额", "毛利率", "等级", "一致性"])
            for d in data["details"]:
                mr = f"{d['rate']:.2%}" if d["rate"] is not None else ""
                ws.append([
                    d["contract_no"], d["city"], d["project_name"],
                    d["front_amount"], d["back_amount"], mr, d["rate_level"] or "", d["similarity"] or "",
                ])

        elif report_type == "acceptance-consistency":
            data = await self.acceptance_consistency_report(db, city)
            ws.title = "验收一致性"
            ws.append(["合同编号", "地市", "项目名称", "一致性"])
            for d in data["details"]:
                ws.append([
                    d["contract_no"], d["city"], d["project_name"], d["similarity"] or "",
                ])

        elif report_type == "low-margin":
            data = await self.low_margin_report(db)
            ws.title = "低毛利项目"
            ws.append(["合同编号", "地市", "项目名称", "前项金额", "后项金额", "毛利率", "等级"])
            for d in data["details"]:
                mr = f"{d['rate']:.2%}" if d["rate"] is not None else ""
                ws.append([
                    d["contract_no"], d["city"], d["project_name"],
                    d["front_amount"], d["back_amount"], mr, d["rate_level"],
                ])

        elif report_type == "high-risk":
            data = await self.high_risk_report(db)
            ws.title = "高风险项目"
            ws.append([
                "合同编号", "地市", "项目名称", "前项金额", "后项金额",
                "毛利率", "等级", "合同一致性", "验收一致性", "项目风险",
            ])
            for d in data["items"]:
                mr = f"{d['rate']:.2%}" if d["rate"] is not None else ""
                ws.append([
                    d["contract_no"], d["city"], d["project_name"],
                    d["front_amount"], d["back_amount"], mr, d["rate_level"] or "",
                    d["contract_similarity"] or "", d["acceptance_similarity"] or "",
                    d["project_risk"] or "",
                ])

        else:
            ws.title = "报表"
            ws.append(["未知报表类型"])

        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output


report_generator = ReportGenerator()
