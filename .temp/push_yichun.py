"""将伊春项目合同关键信息提取.json推送到后端。"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

import httpx
import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_config() -> dict:
    path = Path("A:/Inbox/contract-review-system/agent/config.yaml")
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def _normalize_date(date_str: str) -> str | None:
    """将中文日期转为YYYY-MM-DD格式。如 '2025年5月29日' -> '2025-05-29'。"""
    if not date_str:
        return None
    m = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", date_str)
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m2 = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", date_str)
    if m2:
        return f"{int(m2.group(1)):04d}-{int(m2.group(2)):02d}-{int(m2.group(3)):02d}"
    return None


def _build_terms_text(data: dict, field_name: str) -> str | None:
    """将嵌套条款对象转为可读文本。"""
    if not data or not isinstance(data, dict):
        return str(data) if data else None
    parts = []
    for k, v in data.items():
        if isinstance(v, dict):
            sub = "; ".join(f"{sk}: {sv}" for sk, sv in v.items())
            parts.append(f"{k}: {sub}")
        elif isinstance(v, list):
            parts.append(f"{k}: {', '.join(str(i) for i in v)}")
        else:
            parts.append(f"{k}: {v}")
    return "\n".join(parts) if parts else None


def _build_payment_text(payment: dict) -> str | None:
    """构建付款条款文本。"""
    if not payment:
        return None
    parts = [f"方式: {payment.get('方式', '')}"]
    for stage in payment.get("分期付款", []):
        cond = stage.get("条件", "")
        detail = stage.get("明细", "")
        text = f"{stage['阶段']}: {stage['比例']}"
        if cond:
            text += f", {cond}"
        if detail:
            text += f", {detail}"
        parts.append(text)
    if payment.get("质量保证金"):
        parts.append(f"质量保证金: {payment['质量保证金']}")
    if payment.get("安全生产费"):
        parts.append(f"安全生产费: {payment['安全生产费']}")
    return "\n".join(parts)


def _parse_tax_rate(rate_str: str | None) -> float | None:
    """解析税率字符串。'9%' -> 0.09"""
    if not rate_str:
        return None
    return float(rate_str.replace("%", "")) / 100


def transform_contract(data: dict, contract_type: str, project_no: str) -> dict:
    """将合同数据转为ContractCreate格式。"""
    key = "前项合同" if contract_type == "前项" else "后项合同"
    c = data.get(key, {})
    amount = c.get("合同金额", {})
    party_a = c.get("甲方", {})
    party_b = c.get("乙方", {})

    our_role = "乙方" if contract_type == "前项" else "甲方"

    return {
        "contract_no": project_no,
        "contract_type": contract_type,
        "type_judge_basis": f"伊春项目合同关键信息提取.json - {key}",
        "party_a": party_a.get("名称", ""),
        "party_b": party_b.get("名称", ""),
        "our_role": our_role,
        "signing_date": _normalize_date(c.get("签署日期", "")),
        "total_amount": amount.get("含税价_数字"),
        "amount_uppercase": amount.get("含税价_大写", ""),
        "tax_rate": _parse_tax_rate(amount.get("增值税率")),
        "payment_terms": _build_payment_text(c.get("付款方式", {})),
        "delivery_terms": None,
        "acceptance_terms": _build_terms_text(c.get("验收条款", {}), "验收条款"),
        "breach_terms": _build_terms_text(c.get("违约金条款", {}), "违约金条款"),
        "warranty_terms": _build_terms_text(c.get("质保条款", {}), "质保条款"),
        "ip_terms": None,
        "other_key_terms": c.get("分包转包条款"),
        "source_file_name": "伊春项目合同关键信息提取.json",
        "source_file_hash": "",
        "ocr_raw_text": None,
        "ocr_engine": "manual-extract",
        "llm_model": "manual",
        "line_items": [],
    }


def push_contract(payload: dict, config: dict) -> dict:
    """推送到后端。"""
    base_url = config["server"]["base_url"]
    api_key = config["server"]["api_key"]
    with httpx.Client(base_url=base_url, headers={"X-API-Key": api_key}, timeout=60.0) as client:
        resp = client.post("/contracts", json=payload)
        if resp.status_code >= 400:
            logger.error("推送失败: %s %s", resp.status_code, resp.text)
        resp.raise_for_status()
        return resp.json()


def main() -> None:
    json_path = Path(r"A:\Inbox\contract\恒天项目材料\XYJAEXJCI250500016伊春\6.前后合同、验收报告\伊春项目合同关键信息提取.json")

    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)

    config = load_config()
    project_no = "XYJAEXJCI250500016"

    # 推送前项合同
    front = transform_contract(data, "前项", project_no)
    logger.info("推送前项合同: %s %s→%s 金额=%.2f",
                front["contract_no"], front["party_a"], front["party_b"], front.get("total_amount", 0))
    r1 = push_contract(front, config)
    logger.info("前项结果: %s", r1)

    # 推送后项合同
    back = transform_contract(data, "后项", project_no)
    logger.info("推送后项合同: %s %s→%s 金额=%.2f",
                back["contract_no"], back["party_a"], back["party_b"], back.get("total_amount", 0))
    r2 = push_contract(back, config)
    logger.info("后项结果: %s", r2)

    logger.info("伊春项目推送完成!")


if __name__ == "__main__":
    main()
