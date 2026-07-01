"""比对引擎单元测试。"""

from app.services.comparison_engine import comparison_engine


def test_compare_amount_consistent():
    """差异率 < 5% 视为一致。"""
    result = comparison_engine.compare_amount(1000000, 980000)
    assert result.amount_match == "一致"
    assert result.amount_diff == 20000


def test_compare_amount_inconsistent():
    """差异率 >= 5% 视为不一致。"""
    result = comparison_engine.compare_amount(1000000, 900000)
    assert result.amount_match == "不一致"


def test_compare_amount_zero_front():
    """前项金额为 0 时毛利率无效。"""
    result = comparison_engine.compare_amount(0, 0)
    assert result.amount_match == "无效"
