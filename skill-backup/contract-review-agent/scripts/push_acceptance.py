"""推送已提取的 JSON 验收报告数据到后端 API。

用法：
    python push_acceptance.py --json 验收报告_解析.json --contract-no XYJAEXJCI250500015
    python push_acceptance.py --dir A:\\Inbox\\contract\\恒天项目材料\\  # 批量扫描
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

# 验收报告字段映射（对齐 AcceptanceCreate schema）
FIELD_MAP = {
    "验收编号": "acceptance_no",
    "合同编号": "contract_no",
    "验收类型": "acceptance_type",
    "验收内容": "acceptance_content",
    "验收日期": "acceptance_date",
    "验收结果": "acceptance_result",
}

FRONT_SIGNALS = ["前项", "上家"]
BACK_SIGNALS = ["后项", "下家"]


def load_config(config_path: str = "agent/config.yaml") -> dict:
    """加载配置文件。"""
    path = Path(config_path)
    if not path.exists():
        path = Path("A:/Inbox/contract-review-system/agent/config.yaml")
    if not path.exists():
        logger.error("配置文件不存在: %s", config_path)
        sys.exit(1)
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def map_fields(data: dict) -> dict:
    """映射字段名。"""
    result = {}
    for key, value in data.items():
        mapped_key = FIELD_MAP.get(key, key)
        result[mapped_key] = value
    return result


def judge_acceptance_type(filename: str) -> str:
    """根据文件名判定前后项。"""
    if any(sig in filename for sig in FRONT_SIGNALS):
        return "前项"
    if any(sig in filename for sig in BACK_SIGNALS):
        return "后项"
    return "前项"


def extract_project_no(dir_path: Path) -> str | None:
    """从目录名提取项目编号。"""
    m = re.match(r"([A-Z]{4,}\d+)", dir_path.name)
    return m.group(1) if m else None


def check_duplicate(contract_no: str, acceptance_type: str, base_url: str, api_key: str) -> bool:
    """查重：同编号同类型验收报告是否已存在。返回 True 表示已存在。"""
    with httpx.Client(base_url=base_url, headers={"X-API-Key": api_key}, timeout=30.0) as client:
        resp = client.get("/acceptance/check", params={"contract_no": contract_no, "acceptance_type": acceptance_type})
        resp.raise_for_status()
        return resp.json().get("data", {}).get("exists", False)


def push_acceptance(json_path: Path, config: dict, contract_no: str | None = None) -> dict:
    """推送单个验收报告 JSON 到后端。"""
    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)

    mapped = map_fields(data)

    # 填充必要字段
    if contract_no:
        mapped["contract_no"] = contract_no
    elif "contract_no" not in mapped:
        project_no = extract_project_no(json_path.parent)
        if project_no:
            mapped["contract_no"] = project_no

    if "acceptance_type" not in mapped:
        mapped["acceptance_type"] = judge_acceptance_type(json_path.name)

    mapped.setdefault("type_judge_basis", f"文件名:{json_path.name}")
    mapped.setdefault("source_file_name", json_path.name)

    base_url = config["server"]["base_url"]
    api_key = config["server"]["api_key"]

    # 查重
    if check_duplicate(mapped["contract_no"], mapped["acceptance_type"], base_url, api_key):
        logger.warning("验收报告已存在，跳过: %s / %s", mapped["contract_no"], mapped["acceptance_type"])
        return {"skipped": True, "reason": "duplicate", "contract_no": mapped["contract_no"]}

    with httpx.Client(base_url=base_url, headers={"X-API-Key": api_key}, timeout=60.0) as client:
        resp = client.post("/acceptance", json=mapped)
        resp.raise_for_status()
        return resp.json()


def scan_and_push(dir_path: Path, config: dict) -> list[dict]:
    """扫描目录下所有验收报告 JSON 并推送。"""
    results = []
    patterns = ["*验收*解析*.json", "*验收*_解析.json", "*验收报告*.json"]
    json_files = set()
    for pattern in patterns:
        json_files.update(dir_path.rglob(pattern))

    logger.info("发现 %d 个验收报告 JSON 文件", len(json_files))

    for jf in sorted(json_files):
        try:
            result = push_acceptance(jf, config)
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
    parser = argparse.ArgumentParser(description="推送验收报告 JSON 数据到后端")
    parser.add_argument("--json", help="单个验收报告 JSON 文件路径")
    parser.add_argument("--dir", help="批量扫描目录")
    parser.add_argument("--contract-no", help="强制指定合同编号")
    parser.add_argument("--config", default="agent/config.yaml", help="配置文件路径")
    args = parser.parse_args()

    config = load_config(args.config)

    if args.json:
        result = push_acceptance(Path(args.json), config, args.contract_no)
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
