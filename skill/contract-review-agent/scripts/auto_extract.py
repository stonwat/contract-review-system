"""自动提取并推送合同数据到后端。

智能检测目录结构：
- 如果存在 _解析.json 预提取文件 → 直接推送（流程C）
- 否则 → OCR + LLM 提取后推送（流程A/B）

用法：
    python auto_extract.py --dir A:\\Inbox\\contract\\恒天项目材料\\
    python auto_extract.py --dir A:\\Inbox\\contract\\恒天项目材料\\XYJAEXJCI250500015鹤岗\\
    python auto_extract.py --file A:\\Inbox\\contract\\xxx\\前项合同.pdf
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import re
import sys
from pathlib import Path

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SUPPORTED_EXTS = {".pdf", ".docx", ".doc", ".xls", ".xlsx", ".jpg", ".png"}
CONTRACT_JSON_PATTERNS = ["*合同*解析*.json", "*合同*_解析.json"]
ACCEPTANCE_JSON_PATTERNS = ["*验收*解析*.json", "*验收*_解析.json"]


def extract_project_no(dir_path: Path) -> str | None:
    """从目录名提取项目编号。"""
    m = re.match(r"([A-Z]{4,}\d+)", dir_path.name)
    return m.group(1) if m else None


def file_hash(file_path: Path) -> str:
    """计算文件 SHA256。"""
    h = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def find_pre_extracted(dir_path: Path) -> dict[str, list[Path]]:
    """在目录下查找预提取的 JSON 文件。返回 {类型: [文件列表]}。"""
    result = {"contracts": [], "acceptance": []}

    for pattern in CONTRACT_JSON_PATTERNS:
        result["contracts"].extend(dir_path.rglob(pattern))
    for pattern in ACCEPTANCE_JSON_PATTERNS:
        result["acceptance"].extend(dir_path.rglob(pattern))

    # 去重
    result["contracts"] = list(set(result["contracts"]))
    result["acceptance"] = list(set(result["acceptance"]))
    return result


def judge_type(filename: str) -> str:
    """根据文件名判定前后项。"""
    if any(s in filename for s in ["前项", "上家", "前"]):
        return "前项"
    if any(s in filename for s in ["后项", "下家", "后"]):
        return "后项"
    return "前项"


def map_json_fields(data: dict, is_contract: bool = True) -> dict:
    """映射 JSON 字段名为 API 字段名。"""
    CONTRACT_MAP = {
        "合同编号": "contract_no", "甲方": "party_a", "乙方": "party_b",
        "签订日期": "signing_date", "合同金额": "total_amount",
        "大写金额": "amount_uppercase", "付款条款": "payment_terms",
        "交付条款": "delivery_terms", "验收条款": "acceptance_terms",
        "违约责任": "breach_terms", "质保条款": "warranty_terms",
        "分项清单": "line_items", "项目编号": "item_no",
        "项目名称": "item_name", "单位": "unit", "数量": "quantity",
        "单价": "unit_price", "金额": "amount", "备注": "remark",
    }
    ACCEPTANCE_MAP = {
        "验收编号": "acceptance_no", "合同编号": "contract_no",
        "验收类型": "acceptance_type", "验收内容": "acceptance_content",
        "验收日期": "acceptance_date", "验收结果": "acceptance_result",
    }
    field_map = CONTRACT_MAP if is_contract else ACCEPTANCE_MAP
    mapped = {}
    for key, value in data.items():
        mk = field_map.get(key, key)
        if mk == "line_items" and isinstance(value, list):
            mapped[mk] = [_map_li(item) for item in value]
        else:
            mapped[mk] = value
    return mapped


def _map_li(item: dict) -> dict:
    LI_MAP = {
        "项目编号": "item_no", "项目名称": "item_name", "单位": "unit",
        "数量": "quantity", "单价": "unit_price", "金额": "amount", "备注": "remark",
    }
    return {LI_MAP.get(k, k): v for k, v in item.items()}


def push_json(json_path: Path, is_contract: bool = True, project_no: str | None = None) -> dict:
    """推送 JSON 数据到后端。"""
    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)

    mapped = map_json_fields(data, is_contract)

    if is_contract:
        if project_no and "contract_no" not in mapped:
            mapped["contract_no"] = project_no
        if "contract_type" not in mapped:
            mapped["contract_type"] = judge_type(json_path.name)
        mapped.setdefault("type_judge_basis", f"文件名:{json_path.name}")
        endpoint = "/contracts"
    else:
        if project_no and "contract_no" not in mapped:
            mapped["contract_no"] = project_no
        if "acceptance_type" not in mapped:
            mapped["acceptance_type"] = judge_type(json_path.name)
        mapped.setdefault("type_judge_basis", f"文件名:{json_path.name}")
        endpoint = "/acceptance"

    mapped.setdefault("source_file_name", json_path.name)
    mapped.setdefault("source_file_hash", file_hash(json_path))
    mapped.setdefault("ocr_engine", "pre-extracted")
    mapped.setdefault("llm_model", "unknown")

    with httpx.Client(base_url="http://localhost:8000/api/v1", timeout=60.0) as client:
        resp = client.post(endpoint, json=mapped)
        resp.raise_for_status()
        return resp.json()


async def process_with_ocr_llm(file_path: Path, project_no: str | None = None) -> dict:
    """OCR + LLM 流程已迁移至 paddleocr-doc-parsing skill，此函数保留接口但不再执行。

    如需 OCR 提取，请使用 paddleocr-doc-parsing skill 处理文件后再通过 push_contract / push_acceptance 推送。
    """
    raise NotImplementedError(
        "OCR+LLM 提取已迁移至 paddleocr-doc-parsing skill，"
        "请先使用该 skill 提取结构化数据，再通过 push_contract.py / push_acceptance.py 推送。"
    )


def process_directory(dir_path: Path) -> list[dict]:
    """智能处理目录: 优先使用预提取 JSON，否则跳过（需先通过 OCR skill 提取）。"""
    results = []

    # 查找子项目目录
    subdirs = [d for d in dir_path.iterdir() if d.is_dir()]
    if not subdirs:
        subdirs = [dir_path]

    for subdir in sorted(subdirs):
        project_no = extract_project_no(subdir)
        logger.info("处理子项目: %s (project_no=%s)", subdir.name, project_no)

        # 检测预提取 JSON
        pre = find_pre_extracted(subdir)

        if pre["contracts"] or pre["acceptance"]:
            logger.info("  发现预提取数据，走流程C (直接推送)")
            for jf in pre["contracts"]:
                try:
                    result = push_json(jf, is_contract=True, project_no=project_no)
                    logger.info("  合同推送成功: %s", jf.name)
                    results.append({"file": str(jf), "status": "ok", "type": "contract"})
                except Exception as e:
                    logger.error("  合同推送失败: %s - %s", jf.name, e)
                    results.append({"file": str(jf), "status": "error", "type": "contract", "error": str(e)})

            for jf in pre["acceptance"]:
                try:
                    result = push_json(jf, is_contract=False, project_no=project_no)
                    logger.info("  验收报告推送成功: %s", jf.name)
                    results.append({"file": str(jf), "status": "ok", "type": "acceptance"})
                except Exception as e:
                    logger.error("  验收报告推送失败: %s - %s", jf.name, e)
                    results.append({"file": str(jf), "status": "error", "type": "acceptance", "error": str(e)})
        else:
            logger.warning("  无预提取数据，请先使用 paddleocr-doc-parsing skill 提取")

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="自动提取并推送合同数据")
    parser.add_argument("--dir", help="项目材料根目录")
    parser.add_argument("--file", help="单个合同文件路径")
    args = parser.parse_args()

    if args.file:
        fp = Path(args.file)
        project_no = extract_project_no(fp.parent)
        result = asyncio.run(process_with_ocr_llm(fp, project_no))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.dir:
        results = process_directory(Path(args.dir))
        ok = sum(1 for r in results if r["status"] == "ok")
        err = sum(1 for r in results if r["status"] == "error")
        print(f"\n处理完成: 成功 {ok}, 失败 {err}")
        for r in results:
            status_mark = "OK" if r["status"] == "ok" else "FAIL"
            print(f"  [{status_mark}] {r['file']} ({r.get('type', 'unknown')})")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
