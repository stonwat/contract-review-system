"""比对引擎：数值比对（纯计算）+ LLM 语义比对。"""

from dataclasses import dataclass


@dataclass
class AmountCompareResult:
    front_amount: float
    back_amount: float
    amount_diff: float
    margin_rate: float | None
    amount_match: str  # 一致/不一致


class ComparisonEngine:
    """比对引擎。分两层：数值比对（同步）+ 语义比对（异步调 LLM）。"""

    AMOUNT_MATCH_THRESHOLD = 0.05  # 差异率 < 5% 视为一致

    def compare_amount(
        self, front_amount: float, back_amount: float
    ) -> AmountCompareResult:
        """数值比对：金额差异、毛利率。"""
        diff = front_amount - back_amount
        margin_rate = diff / front_amount if front_amount else None
        if margin_rate is None:
            amount_match = "无效"
        else:
            amount_match = (
                "一致" if abs(margin_rate) < self.AMOUNT_MATCH_THRESHOLD else "不一致"
            )
        return AmountCompareResult(
            front_amount=front_amount,
            back_amount=back_amount,
            amount_diff=diff,
            margin_rate=margin_rate,
            amount_match=amount_match,
        )


comparison_engine = ComparisonEngine()
