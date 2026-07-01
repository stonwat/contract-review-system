"""风险评估：根据比对结果自动生成风险记录。"""

from app.services.comparison_engine import AmountCompareResult


class RiskEvaluator:
    """风险判定规则引擎。"""

    LOW_MARGIN_HIGH = 0.03  # 毛利率 < 3% 视为低毛利（高风险）
    LOW_MARGIN_MEDIUM = 0.05  # 3% ~ 5% 视为低毛利（中风险）
    OVER_SUBCONTRACT_RATIO = 1.1  # 后项数量超过前项 110% 视为超量分包

    def evaluate_margin(self, margin_rate: float | None) -> tuple[str | None, str | None]:
        """根据毛利率判定风险类型和等级。返回 (risk_type, risk_level)。"""
        if margin_rate is None:
            return None, None
        if margin_rate < 0:
            return "利润倒挂", "高"
        if margin_rate < self.LOW_MARGIN_HIGH:
            return "低毛利", "高"
        if margin_rate < self.LOW_MARGIN_MEDIUM:
            return "低毛利", "中"
        return None, None

    def evaluate_subcontract(
        self, front_qty: float, back_qty: float
    ) -> tuple[str | None, str | None]:
        """超量分包判定。"""
        if back_qty > front_qty * self.OVER_SUBCONTRACT_RATIO:
            return "超量分包", "中"
        return None, None

    def evaluate_price_inversion(
        self, front_price: float, back_price: float
    ) -> tuple[str | None, str | None]:
        """单价倒挂判定。"""
        if back_price > front_price:
            return "单价倒挂", "高"
        return None, None


risk_evaluator = RiskEvaluator()
