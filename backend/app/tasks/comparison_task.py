"""异步任务：合同比对。骨架，实际通过 arq 投递执行。"""

from app.services.comparison_engine import comparison_engine


async def run_comparison_task(comparison_id: str) -> None:
    """比对任务：数值比对 + LLM 语义比对。骨架。"""
    _ = comparison_engine
    # 实际实现：
    # 1. 取出前后项合同及分项清单
    # 2. 数值比对（金额、毛利率、分项差异）
    # 3. LLM 语义比对（付款/交付/验收/违约条款）
    # 4. 写入 comparisons + line_item_comparisons
    # 5. 触发风险判定，写入 risk_records
