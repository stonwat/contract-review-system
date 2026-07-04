"""批量推送恒天项目关键信息提取JSON到后端。

支持伊春和哈尔滨的关键信息提取JSON格式。
"""

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


def _normalize_date(date_str: str | None) -> str | None:
    if not date_str:
        return None
    m = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", date_str)
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m2 = re.match(r"(\d{4})[-./](\d{1,2})[-./](\d{1,2})", date_str)
    if m2:
        return f"{int(m2.group(1)):04d}-{int(m2.group(2)):02d}-{int(m2.group(3)):02d}"
    return None


def _build_terms_text(data) -> str | None:
    if not data:
        return None
    if isinstance(data, str):
        return data
    if not isinstance(data, dict):
        return str(data)
    parts = []
    for k, v in data.items():
        if isinstance(v, dict):
            sub = "; ".join(f"{sk}: {sv}" for sk, sv in v.items())
            parts.append(f"{k}: {sub}")
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    sub = "; ".join(f"{sk}: {sv}" for sk, sv in item.items())
                    parts.append(sub)
                else:
                    parts.append(str(item))
        else:
            parts.append(f"{k}: {v}")
    return "\n".join(parts) if parts else None


def _build_payment_text(payment: dict) -> str | None:
    if not payment:
        return None
    parts = []
    if payment.get("方式"):
        parts.append(f"方式: {payment['方式']}")
    for stage in payment.get("分期付款", []):
        cond = stage.get("条件", "")
        text = f"{stage['阶段']}: {stage['比例']}"
        if cond:
            text += f", {cond}"
        parts.append(text)
    if payment.get("质量保证金"):
        parts.append(f"质量保证金: {payment['质量保证金']}")
    if payment.get("安全生产费"):
        parts.append(f"安全生产费: {payment['安全生产费']}")
    return "\n".join(parts) if parts else None


def _parse_tax_rate(rate_str) -> float | None:
    if not rate_str:
        return None
    if isinstance(rate_str, (int, float)):
        return float(rate_str) / 100 if float(rate_str) > 1 else float(rate_str)
    return float(str(rate_str).replace("%", "")) / 100


def _get_amount(amount_data: dict) -> float | None:
    """兼容不同JSON格式的金额字段名。"""
    for key in ["含税价_数字", "签约合同价_含税", "含税价", "合同金额"]:
        if key in amount_data:
            val = amount_data[key]
            if isinstance(val, (int, float)):
                return float(val)
    return None


def _get_amount_uppercase(amount_data: dict) -> str | None:
    for key in ["含税价_大写", "签约合同价_含税_大写"]:
        if key in amount_data:
            return str(amount_data[key])
    return None


def transform_contract(c: dict, contract_type: str, project_no: str) -> dict:
    """将单个合同数据（前项或后项）转为ContractCreate格式。"""
    amount = c.get("合同金额", {})
    party_a = c.get("甲方", {})
    party_b = c.get("乙方", {})
    our_role = "乙方" if contract_type == "前项" else "甲方"

    # 签约日期
    signing_date = _normalize_date(c.get("签署日期") or c.get("签订日期") or c.get("签约日期"))

    # 工期
    period_data = c.get("工期", {})
    contract_period = None
    if isinstance(period_data, dict):
        days = period_data.get("总日历天数") or period_data.get("合同工期总日历天数") or period_data.get("约定")
        unit = period_data.get("单位", "天")
        if days:
            contract_period = f"{days}{unit}" if unit else str(days)

    payment = c.get("付款方式", {})

    return {
        "contract_no": project_no,
        "contract_type": contract_type,
        "type_judge_basis": f"关键信息提取JSON - {contract_type}合同",
        "party_a": party_a.get("名称", "") if isinstance(party_a, dict) else str(party_a),
        "party_b": party_b.get("名称", "") if isinstance(party_b, dict) else str(party_b),
        "our_role": our_role,
        "signing_date": signing_date,
        "contract_period": contract_period,
        "total_amount": _get_amount(amount),
        "amount_uppercase": _get_amount_uppercase(amount),
        "tax_rate": _parse_tax_rate(amount.get("增值税率")),
        "payment_terms": _build_payment_text(payment) if isinstance(payment, dict) else None,
        "delivery_terms": None,
        "acceptance_terms": _build_terms_text(c.get("验收条款")),
        "breach_terms": _build_terms_text(c.get("违约金条款")),
        "warranty_terms": _build_terms_text(c.get("质保条款")),
        "ip_terms": None,
        "other_key_terms": _build_terms_text(c.get("分包转包条款")),
        "source_file_name": "关键信息提取JSON",
        "source_file_hash": "",
        "ocr_raw_text": None,
        "ocr_engine": "manual-extract",
        "llm_model": "manual",
        "line_items": [],
    }


def push_contract(payload: dict, config: dict) -> dict:
    base_url = config["server"]["base_url"]
    api_key = config["server"]["api_key"]
    with httpx.Client(base_url=base_url, headers={"X-API-Key": api_key}, timeout=60.0) as client:
        resp = client.post("/contracts", json=payload)
        if resp.status_code >= 400:
            logger.error("推送失败: %s %s", resp.status_code, resp.text[:500])
        resp.raise_for_status()
        return resp.json()


def push_acceptance(report_data: dict, project_no: str, acceptance_type: str, config: dict) -> dict:
    """推送验收报告到后端。"""
    payload = {
        "acceptance_no": f"YS-{project_no}",
        "contract_no": project_no,
        "acceptance_type": acceptance_type,
        "type_judge_basis": f"关键信息提取JSON - {acceptance_type}验收报告",
        "acceptance_content": _build_terms_text(report_data),
        "acceptance_date": _normalize_date(
            report_data.get("验收日期") or report_data.get("甲方签署日期") or report_data.get("完工验收报告", {}).get("甲方签署日期")
        ),
        "acceptance_result": report_data.get("验收结论") or report_data.get("验收意见") or "合格",
        "source_file_name": "关键信息提取JSON",
        "source_file_hash": "",
        "ocr_raw_text": None,
        "ocr_engine": "manual-extract",
        "llm_model": "manual",
    }
    base_url = config["server"]["base_url"]
    api_key = config["server"]["api_key"]
    with httpx.Client(base_url=base_url, headers={"X-API-Key": api_key}, timeout=60.0) as client:
        resp = client.post("/acceptance", json=payload)
        if resp.status_code >= 400:
            logger.error("推送失败: %s %s", resp.status_code, resp.text[:500])
        resp.raise_for_status()
        return resp.json()


def process_project(json_path: Path, project_no: str, config: dict) -> None:
    """处理单个项目的关键信息提取JSON。"""
    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)

    city = data.get("项目名称", "").split("（")[-1].split("）")[0] if "（" in data.get("项目名称", "") else ""

    # 前项合同
    fc = data.get("前项合同")
    if fc:
        front = transform_contract(fc, "前项", project_no)
        logger.info("  推送前项合同: %s→%s 金额=%s", front["party_a"][:8], front["party_b"][:8], front.get("total_amount"))
        r = push_contract(front, config)
        logger.info("  前项结果: %s", r.get("data", {}).get("contract_id", "error"))

    # 后项合同
    bc = data.get("后项合同")
    if bc:
        back = transform_contract(bc, "后项", project_no)
        logger.info("  推送后项合同: %s→%s 金额=%s", back["party_a"][:8], back["party_b"][:8], back.get("total_amount"))
        r = push_contract(back, config)
        logger.info("  后项结果: %s", r.get("data", {}).get("contract_id", "error"))

    # 前项验收报告
    facc = data.get("前项验收报告")
    if facc:
        logger.info("  推送前项验收报告")
        r = push_acceptance(facc, project_no, "前项", config)
        logger.info("  前项验收结果: %s", r.get("data", {}).get("acceptance_id", "error"))

    # 后项验收报告
    bacc = data.get("后项验收报告")
    if bacc:
        logger.info("  推送后项验收报告")
        r = push_acceptance(bacc, project_no, "后项", config)
        logger.info("  后项验收结果: %s", r.get("data", {}).get("acceptance_id", "error"))


# 项目配置
PROJECTS = {
    "XYJAEXJCI250500016": Path(r"A:\Inbox\contract\恒天项目材料\XYJAEXJCI250500016伊春\6.前后合同、验收报告\伊春项目合同关键信息提取.json"),
    "XYJAEXJCI250500018": Path(r"A:\Inbox\contract\恒天项目材料\XYJAEXJCI250500018哈尔滨\6.前后合同、验收报告\哈尔滨_合同关键信息提取.json"),
}


def main() -> None:
    config = load_config()

    for project_no, json_path in PROJECTS.items():
        if not json_path.exists():
            logger.warning("文件不存在: %s", json_path)
            continue
        logger.info("=" * 60)
        logger.info("处理项目: %s (%s)", project_no, json_path.parent.parent.name)
        try:
            process_project(json_path, project_no, config)
        except Exception as e:
            logger.error("项目处理失败: %s - %s", project_no, e)

    logger.info("=" * 60)
    logger.info("全部处理完成!")


if __name__ == "__main__":
    main()
