"""数据库 DDL 迁移脚本：对齐 V3.2 设计。

执行方式：
    python backend/scripts/migrate_v3_2.py

功能：
    1. 删除旧表 line_items（如存在）
    2. 删除 projects 表中的旧字段（status, risk_level, gross_margin_rate, gross_margin_level, front_amount, back_amount）
    3. 创建 contract_analysis 表（如不存在）
    4. 创建 acceptance_report_analysis 表（如不存在）
    5. 验证最终表结构
"""

import asyncio
import sys
from pathlib import Path

# 将 backend 目录加入 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from app.db.database import engine


async def check_column_exists(conn, table: str, column: str) -> bool:
    """检查列是否存在。"""
    result = await conn.execute(
        text(
            "SELECT EXISTS ("
            "  SELECT 1 FROM information_schema.columns "
            "  WHERE table_name = :table AND column_name = :column"
            ")"
        ),
        {"table": table, "column": column},
    )
    return result.scalar()


async def check_table_exists(conn, table: str) -> bool:
    """检查表是否存在。"""
    result = await conn.execute(
        text(
            "SELECT EXISTS ("
            "  SELECT 1 FROM information_schema.tables "
            "  WHERE table_name = :table"
            ")"
        ),
        {"table": table},
    )
    return result.scalar()


async def migrate():
    print("=" * 60)
    print("数据库 V3.2 迁移脚本")
    print("=" * 60)

    async with engine.begin() as conn:
        # ── 1. 删除旧表 line_items ──
        if await check_table_exists(conn, "line_items"):
            print("[1/5] 删除旧表 line_items ...")
            await conn.execute(text("DROP TABLE IF EXISTS line_items CASCADE"))
            print("      ✓ 已删除")
        else:
            print("[1/5] line_items 表不存在，跳过")

        # ── 2. 删除 projects 旧字段 ──
        old_columns = [
            "status",
            "risk_level",
            "gross_margin_rate",
            "gross_margin_level",
            "front_amount",
            "back_amount",
        ]
        print("[2/5] 检查 projects 表旧字段 ...")
        for col in old_columns:
            if await check_column_exists(conn, "projects", col):
                print(f"      删除 projects.{col} ...")
                await conn.execute(text(f"ALTER TABLE projects DROP COLUMN IF EXISTS {col}"))
                print(f"      ✓ 已删除 projects.{col}")
            else:
                print(f"      projects.{col} 不存在，跳过")

        # ── 3. 创建 contract_analysis 表 ──
        print("[3/5] 检查 contract_analysis 表 ...")
        if not await check_table_exists(conn, "contract_analysis"):
            await conn.execute(text("""
                CREATE TABLE contract_analysis (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    contract_no VARCHAR(100) NOT NULL REFERENCES projects(contract_no),
                    rate NUMERIC(6, 4),
                    rate_level VARCHAR(20),
                    similarity VARCHAR(20),
                    analysis TEXT,
                    verified BOOLEAN NOT NULL DEFAULT FALSE,
                    verified_by VARCHAR(50),
                    verified_at TIMESTAMPTZ,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    CONSTRAINT uq_contract_analysis_no UNIQUE (contract_no),
                    CONSTRAINT ck_ca_rate_level CHECK (rate_level IN ('正常', '低毛利', '利润倒挂')),
                    CONSTRAINT ck_ca_similarity CHECK (similarity IN ('完全一致', '有一致性风险', '完全不一致'))
                )
            """))
            await conn.execute(text(
                "CREATE INDEX idx_contract_analysis_no ON contract_analysis (contract_no)"
            ))
            print("      ✓ 已创建 contract_analysis 表")
        else:
            print("      contract_analysis 表已存在，跳过")

        # ── 4. 创建 acceptance_report_analysis 表 ──
        print("[4/5] 检查 acceptance_report_analysis 表 ...")
        if not await check_table_exists(conn, "acceptance_report_analysis"):
            await conn.execute(text("""
                CREATE TABLE acceptance_report_analysis (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    contract_no VARCHAR(100) NOT NULL REFERENCES projects(contract_no),
                    similarity VARCHAR(20),
                    analysis TEXT,
                    verified BOOLEAN NOT NULL DEFAULT FALSE,
                    verified_by VARCHAR(50),
                    verified_at TIMESTAMPTZ,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    CONSTRAINT uq_acceptance_analysis_no UNIQUE (contract_no),
                    CONSTRAINT ck_ara_similarity CHECK (similarity IN ('完全一致', '有一致性风险', '完全不一致'))
                )
            """))
            await conn.execute(text(
                "CREATE INDEX idx_acceptance_analysis_no ON acceptance_report_analysis (contract_no)"
            ))
            print("      ✓ 已创建 acceptance_report_analysis 表")
        else:
            print("      acceptance_report_analysis 表已存在，跳过")

        # ── 5. 验证最终表结构 ──
        print("[5/5] 验证表结构 ...")
        tables = ["projects", "contracts", "acceptance_reports",
                  "contract_analysis", "acceptance_report_analysis", "admins"]
        for t in tables:
            exists = await check_table_exists(conn, t)
            status = "✓" if exists else "✗"
            print(f"      {status} {t}")

        # 检查 line_items 是否已删除
        if await check_table_exists(conn, "line_items"):
            print("      ✗ line_items 仍存在（异常）")
        else:
            print("      ✓ line_items 已删除")

    print("\n" + "=" * 60)
    print("迁移完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(migrate())
