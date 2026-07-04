"""推送已提取的 JSON 合同数据到后端 API。

用法：
    python push_contract.py --json 前项合同_解析.json --contract-type 前项 --contract-no XYJAEXJCI250500015
    python push_contract.py --dir A:\\Inbox\\contract\\恒天项目材料\\  # 批量扫描所有 _解析.json
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path

import httpx
import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# JSON 字段名到 API 字段名的映射（兼容中文字段名）
FIELD_MAP = {
    "合同编号": "contract_no",
    "项目名称": "project_name",
    "地市": "city",
    "甲方": "party_a",
    "乙方": "party_b",
    "我方角色": "our_role",
    "签订日期": "signing_date",
    "工期": "contract_period",
    "合同金额": "total_amount",
    "大写金额": "amount_uppercase",
    "税率": "tax_rate",
    "付款条款": "payment_terms",
    "交付条款": "delivery_terms",
    "验收条款": "acceptance_terms",
    "违约责任": "breach_terms",
    "质保条款": "warranty_terms",
    "知识产权条款": "ip_terms",
    "其他关键条款": "other_key_terms",
}

# 文件名前后项信号
FRONT_SIGNALS = ["前项", "上家"]
BACK_SIGNALS = ["后项", "下家"]


def load_config(config_path: str = "agent/config.yaml") -> dict:
    """加载配置文件。"""
    path = Path(config_path)
    if not path.exists():
        # 尝试项目根目录
        path = Path("A:/Inbox/contract-review-system/agent/config.yaml")
    if not path.exists():
        logger.error("配置文件不存在: %s", config_path)
        sys.exit(1)
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def map_fields(data: dict) -> dict:
    """将 JSON 中的中文/自定义字段名映射为 API 字段名。"""
    result = {}
    for key, value in data.items():
        mapped_key = FIELD_MAP.get(key, key)
        result[mapped_key] = value
    return result


def judge_contract_type(filename: str) -> str:
    """根据文件名判定前后项。"""
    if any(sig in filename for sig in FRONT_SIGNALS):
        return "前项"
    if any(sig in filename for sig in BACK_SIGNALS):
        return "后项"
    return "前项"  # 默认


def extract_project_no(dir_path: Path) -> str | None:
    """从目录名提取项目编号。如 XYJAEXJCI250500015鹤岗 → XYJAEXJCI250500015。"""
    m = re.match(r"([A-Z]{4,}\d+)", dir_path.name)
    return m.group(1) if m else None


def check_duplicate(contract_no: str, contract_type: str, base_url: str, api_key: str) -> bool:
    """查重：同编号同类型合同是否已存在。返回 True 表示已存在。"""
    with httpx.Client(base_url=base_url, headers={"X-API-Key": api_key}, timeout=30.0) as client:
        resp = client.get("/contracts/check", params={"contract_no": contract_no, "contract_type": contract_type})
        resp.raise_for_status()
        return resp.json().get("data", {}).get("exists", False)


def push_contract(json_path: Path, config: dict, contract_type: str | None = None, contract_no: str | None = None) -> dict:
    """推送单个合同 JSON 到后端。"""
    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)

    # 字段映射
    mapped = map_fields(data)

    # 填充必要字段
    if contract_type:
        mapped["contract_type"] = contract_type
    elif "contract_type" not in mapped:
        mapped["contract_type"] = judge_contract_type(json_path.name)

    if contract_no:
        mapped["contract_no"] = contract_no
    elif "contract_no" not in mapped:
        # 尝试从目录名提取
        project_no = extract_project_no(json_path.parent)
        if project_no:
            mapped["contract_no"] = project_no

    mapped.setdefault("type_judge_basis", f"文件名:{json_path.name}")
    mapped.setdefault("source_file_name", json_path.name)

    # 推送
    base_url = config["server"]["base_url"]
    api_key = config["server"]["api_key"]

    # 查重
    if check_duplicate(mapped["contract_no"], mapped["contract_type"], base_url, api_key):
        logger.warning("合同已存在，跳过: %s / %s", mapped["contract_no"], mapped["contract_type"])
        return {"skipped": True, "reason": "duplicate", "contract_no": mapped["contract_no"]}

    with httpx.Client(base_url=base_url, headers={"X-API-Key": api_key}, timeout=60.0) as client:
        resp = client.post("/contracts", json=mapped)
        resp.raise_for_status()
        return resp.json()


def scan_and_push(dir_path: Path, config: dict) -> list[dict]:
    """扫描目录下所有合同 _解析.json 并推送。"""
    results = []
    # 查找合同相关的 JSON 文件
    patterns = ["*合同*解析*.json", "*合同*_解析.json", "*合同*.json"]
    json_files = set()
    for pattern in patterns:
        json_files.update(dir_path.rglob(pattern))

    logger.info("发现 %d 个合同 JSON 文件", len(json_files))

    for jf in sorted(json_files):
        # 跳过验收报告
        if "验收" in jf.name:
            continue
        try:
            result = push_contract(jf, config)
            if result.get("skipped"):
                logger.info("跳过重复: %s", jf.name)
            else:
                logger.info("推送成功: %s -> %s", jf.name, result.get("data"))
            results.append({"file": str(jf), "status": "ok", "result": result})
        except Exception as e:
            logger.error("推送失败: %s, 错误: %s", jf.name, e)
            results.append({"file": str(jf), "status": "error", "error": str(e)})

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="推送合同 JSON 数据到后端")
    parser.add_argument("--json", help="单个合同 JSON 文件路径")
    parser.add_argument("--dir", help="批量扫描目录")
    parser.add_argument("--contract-type", choices=["前项", "后项"], help="强制指定前后项")
    parser.add_argument("--contract-no", help="强制指定合同编号")
    parser.add_argument("--config", default="agent/config.yaml", help="配置文件路径")
    args = parser.parse_args()

    config = load_config(args.config)

    if args.json:
        result = push_contract(Path(args.json), config, args.contract_type, args.contract_no)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.dir:
        results = scan_and_push(Path(args.dir), config)
        ok = sum(1 for r in results if r["status"] == "ok")
        err = sum(1 for r in results if r["status"] == "error")
        print(f"\n完成: 成功 {ok}, 失败 {err}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
