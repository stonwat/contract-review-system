"""回算现有项目的毛利率。"""
import asyncio
import sys
sys.path.insert(0, r"A:\Inbox\contract-review-system\backend")

async def main():
    from app.db.database import engine
    from sqlalchemy import text
    
    async with engine.begin() as conn:
        # 回算毛利率
        result = await conn.execute(text("""
            UPDATE projects p
            SET 
              gross_margin_rate = sub.rate,
              gross_margin_level = CASE 
                WHEN sub.rate < 0 THEN '利润倒挂'
                WHEN sub.rate < 0.05 THEN '低毛利'
                ELSE '正常'
              END,
              risk_level = CASE 
                WHEN sub.rate < 0 THEN '利润倒挂'
                WHEN sub.rate < 0.05 THEN '低毛利'
                ELSE '正常'
              END
            FROM (
              SELECT 
                f.contract_no,
                (f.total_amount - b.total_amount) / f.total_amount AS rate
              FROM contracts f
              JOIN contracts b ON f.contract_no = b.contract_no 
                AND b.contract_type = '后项'
                AND f.contract_type = '前项'
              WHERE f.total_amount IS NOT NULL 
                AND b.total_amount IS NOT NULL
                AND f.total_amount > 0
            ) sub
            WHERE p.contract_no = sub.contract_no
        """))
        print(f"Updated {result.rowcount} projects with margin rates")
        
        # 查看结果
        rows = await conn.execute(text("SELECT contract_no, gross_margin_rate, gross_margin_level FROM projects"))
        for row in rows:
            print(f"  {row[0]}: rate={row[1]}, level={row[2]}")

asyncio.run(main())
