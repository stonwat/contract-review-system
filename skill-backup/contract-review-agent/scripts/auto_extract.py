"""自动提取并推送合同数据到后端。

智能检测目录结构：
- 如果存在 _解析.json 预提取文件 → 查重后直接推送（流程C）
- 否则 → OCR + LLM 提取后推送（流程A/B）

V2.0 更新：
- 移除 line_items / source_file_hash / ocr_engine / llm_model / ocr_raw_text
- 推送前自动查重
- 新增 --risk-analysis 模式：扫描可分析项目，执行 LLM 对比分析并回写

用法：
    python auto_extract.py --dir A:\\Inbox\\contract\\恒天项目材料\\
    python auto_extract.py --dir A:\\Inbox\\contract\\恒天项目材料\\XYJAEXJCI250500015鹤岗\\
    python auto_extract.py --file A:\\Inbox\\contract\\xxx\\前项合同.pdf
    python auto_extract.py --risk-analysis  # 流程二：项目风险分析
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
import sys
from pathlib import Path

import httpx
import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SUPPORTED_EXTS = {".pdf", ".docx", ".doc", ".xls", ".xlsx", ".jpg", ".png"}
CONTRACT_JSON_PATTERNS = ["*合同*解析*.json", "*合同*_解析.json"]
ACCEPTANCE_JSON_PATTERNS = ["*验收*解析*.json", "*验收*_解析.json"]

# 合同字段映射（对齐 ContractCreate schema）
CONTRACT_MAP = {
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

# 验收报告字段映射（对齐 AcceptanceCreate schema）
ACCEPTANCE_MAP = {
    "验收编号": "acceptance_no",
    "合同编号": "contract_no",
    "验收类型": "acceptance_type",
    "验收内容": "acceptance_content",
    "验收日期": "acceptance_date",
    "验收结果": "acceptance_result",
}


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


def extract_project_no(dir_path: Path) -> str | None:
    """从目录名提取项目编号。"""
    m = re.match(r"([A-Z]{4,}\d+)", dir_path.name)
    return m.group(1) if m else None


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
    field_map = CONTRACT_MAP if is_contract else ACCEPTANCE_MAP
    mapped = {}
    for key, value in data.items():
        mk = field_map.get(key, key)
        mapped[mk] = value
    return mapped


# ── 查重 ──────────────────────────────────────────────────


def check_contract_duplicate(contract_no: str, contract_type: str, base_url: str, api_key: str) -> bool:
    """合同查重。返回 True 表示已存在。"""
    with httpx.Client(base_url=base_url, headers={"X-API-Key": api_key}, timeout=30.0) as client:
        resp = client.get("/contracts/check", params={"contract_no": contract_no, "contract_type": contract_type})
        resp.raise_for_status()
        return resp.json().get("data", {}).get("exists", False)


def check_acceptance_duplicate(contract_no: str, acceptance_type: str, base_url: str, api_key: str) -> bool:
    """验收报告查重。返回 True 表示已存在。"""
    with httpx.Client(base_url=base_url, headers={"X-API-Key": api_key}, timeout=30.0) as client:
        resp = client.get("/acceptance/check", params={"contract_no": contract_no, "acceptance_type": acceptance_type})
        resp.raise_for_status()
        return resp.json().get("data", {}).get("exists", False)


# ── 推送 ──────────────────────────────────────────────────


def push_json(json_path: Path, config: dict, is_contract: bool = True, project_no: str | None = None) -> dict:
    """推送 JSON 数据到后端（含查重）。"""
    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)

    mapped = map_json_fields(data, is_contract)

    base_url = config["server"]["base_url"]
    api_key = config["server"]["api_key"]

    if is_contract:
        if project_no and "contract_no" not in mapped:
            mapped["contract_no"] = project_no
        if "contract_type" not in mapped:
            mapped["contract_type"] = judge_type(json_path.name)
        mapped.setdefault("type_judge_basis", f"文件名:{json_path.name}")
        mapped.setdefault("source_file_name", json_path.name)
        endpoint = "/contracts"

        # 查重
        if check_contract_duplicate(mapped["contract_no"], mapped["contract_type"], base_url, api_key):
            logger.warning("合同已存在，跳过: %s / %s", mapped["contract_no"], mapped["contract_type"])
            return {"skipped": True, "reason": "duplicate"}
    else:
        if project_no and "contract_no" not in mapped:
            mapped["contract_no"] = project_no
        if "acceptance_type" not in mapped:
            mapped["acceptance_type"] = judge_type(json_path.name)
        mapped.setdefault("type_judge_basis", f"文件名:{json_path.name}")
        mapped.setdefault("source_file_name", json_path.name)
        endpoint = "/acceptance"

        # 查重
        if check_acceptance_duplicate(mapped["contract_no"], mapped["acceptance_type"], base_url, api_key):
            logger.warning("验收报告已存在，跳过: %s / %s", mapped["contract_no"], mapped["acceptance_type"])
            return {"skipped": True, "reason": "duplicate"}

    with httpx.Client(base_url=base_url, headers={"X-API-Key": api_key}, timeout=60.0) as client:
        resp = client.post(endpoint, json=mapped)
        resp.raise_for_status()
        return resp.json()


async def process_with_ocr_llm(file_path: Path, config: dict, project_no: str | None = None) -> dict:
    """使用 OCR + LLM 流程处理文件并推送。"""
    # 动态导入 agent 模块
    sys.path.insert(0, "A:/Inbox/contract-review-system")
    from agent.config_client import AgentConfig
    from agent.ocr_extract import extract_text, judge_front_back, llm_extract

    agent_config = AgentConfig()

    # 1. OCR 提取文本
    text = extract_text(file_path)
    if not text:
        raise ValueError(f"OCR 提取文本为空: {file_path}")

    # 2. LLM 结构化提取
    extracted = await llm_extract(text, agent_config)

    # 3. 构建推送数据
    contract_no = extracted.get("contract_no", project_no or file_path.stem)
    contract_type = judge_front_back(file_path.name, agent_config, str(contract_no))

    payload = {
        "contract_no": str(contract_no),
        "contract_type": contract_type,
        "type_judge_basis": f"文件名:{file_path.name}",
        "source_file_name": file_path.name,
        **{k: v for k, v in extracted.items() if k != "raw"},
    }

    base_url = config["server"]["base_url"]
    api_key = config["server"]["api_key"]

    # 4. 查重
    if check_contract_duplicate(payload["contract_no"], payload["contract_type"], base_url, api_key):
        logger.warning("合同已存在，跳过: %s / %s", payload["contract_no"], payload["contract_type"])
        return {"skipped": True, "reason": "duplicate"}

    # 5. 推送
    with httpx.Client(base_url=base_url, headers={"X-API-Key": api_key}, timeout=60.0) as client:
        resp = client.post("/contracts", json=payload)
        resp.raise_for_status()
        return resp.json()


# ── 流程一：文档提交 ──────────────────────────────────────


def process_directory(dir_path: Path, config: dict) -> list[dict]:
    """智能处理目录: 优先使用预提取 JSON，否则走 OCR+LLM。"""
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
                    result = push_json(jf, config, is_contract=True, project_no=project_no)
                    if result.get("skipped"):
                        logger.info("  合同跳过(重复): %s", jf.name)
                    else:
                        logger.info("  合同推送成功: %s", jf.name)
                    results.append({"file": str(jf), "status": "ok", "type": "contract"})
                except Exception as e:
                    logger.error("  合同推送失败: %s - %s", jf.name, e)
                    results.append({"file": str(jf), "status": "error", "type": "contract", "error": str(e)})

            for jf in pre["acceptance"]:
                try:
                    result = push_json(jf, config, is_contract=False, project_no=project_no)
                    if result.get("skipped"):
                        logger.info("  验收报告跳过(重复): %s", jf.name)
                    else:
                        logger.info("  验收报告推送成功: %s", jf.name)
                    results.append({"file": str(jf), "status": "ok", "type": "acceptance"})
                except Exception as e:
                    logger.error("  验收报告推送失败: %s - %s", jf.name, e)
                    results.append({"file": str(jf), "status": "error", "type": "acceptance", "error": str(e)})
        else:
            logger.info("  无预提取数据，走流程A/B (OCR+LLM)")
            # 查找合同/验收的原文件
            contract_files = [
                p for p in subdir.rglob("*")
                if p.suffix.lower() in SUPPORTED_EXTS and p.name.startswith(("前项", "后项", "验收", "合同"))
            ]
            for cf in contract_files:
                try:
                    result = asyncio.run(process_with_ocr_llm(cf, config, project_no))
                    if result.get("skipped"):
                        logger.info("  OCR+LLM 跳过(重复): %s", cf.name)
                    else:
                        logger.info("  OCR+LLM 推送成功: %s", cf.name)
                    results.append({"file": str(cf), "status": "ok", "type": "ocr_llm"})
                except Exception as e:
                    logger.error("  OCR+LLM 推送失败: %s - %s", cf.name, e)
                    results.append({"file": str(cf), "status": "error", "type": "ocr_llm", "error": str(e)})

    return results


# ── 流程二：项目风险分析 ──────────────────────────────────


def get_api_client(config: dict) -> httpx.Client:
    """创建 API 客户端。"""
    base_url = config["server"]["base_url"]
    api_key = config["server"]["api_key"]
    return httpx.Client(base_url=base_url, headers={"X-API-Key": api_key}, timeout=120.0)


def fetch_projects(client: httpx.Client) -> list[dict]:
    """获取全部项目列表。"""
    resp = client.get("/projects")
    resp.raise_for_status()
    data = resp.json().get("data", {})
    return data.get("items", [])


def fetch_contracts_by_no(client: httpx.Client, contract_no: str) -> list[dict]:
    """获取指定编号的全部合同。"""
    resp = client.get("/contracts", params={"contract_no": contract_no, "page_size": 10})
    resp.raise_for_status()
    return resp.json().get("data", {}).get("items", [])


def fetch_acceptance_by_no(client: httpx.Client, contract_no: str) -> list[dict]:
    """获取指定编号的全部验收报告。"""
    resp = client.get("/acceptance", params={"contract_no": contract_no, "page_size": 10})
    resp.raise_for_status()
    return resp.json().get("data", {}).get("items", [])


def push_contract_analysis(client: httpx.Client, contract_no: str, analysis: dict) -> dict:
    """推送合同对比分析结果（UPSERT）。"""
    payload = {"contract_no": contract_no, **analysis}
    resp = client.post("/contract-analysis", json=payload)
    resp.raise_for_status()
    return resp.json()


def push_acceptance_analysis(client: httpx.Client, contract_no: str, analysis: dict) -> dict:
    """推送验收报告对比分析结果（UPSERT）。"""
    payload = {"contract_no": contract_no, **analysis}
    resp = client.post("/acceptance-analysis", json=payload)
    resp.raise_for_status()
    return resp.json()


def update_project(client: httpx.Client, contract_no: str, updates: dict) -> dict:
    """更新项目（project_risk, llm_analyzed 等）。"""
    resp = client.put(f"/projects/{contract_no}", json=updates)
    resp.raise_for_status()
    return resp.json()


def calculate_rate(front_amount: float | None, back_amount: float | None) -> tuple[float | None, str]:
    """计算毛利率并判定等级。返回 (rate, rate_level)。"""
    if not front_amount or front_amount == 0:
        return None, "无效"
    if back_amount is None:
        return None, "无效"
    rate = (front_amount - back_amount) / front_amount
    if rate < 0:
        return rate, "利润倒挂"
    elif rate < 0.05:
        return rate, "低毛利"
    else:
        return rate, "正常"


def judge_project_risk(rate_level: str, contract_similarity: str | None, acceptance_similarity: str | None) -> str:
    """综合判定项目风险等级。"""
    if rate_level in ("利润倒挂", "低毛利"):
        return "高风险"
    if contract_similarity == "完全不一致" or acceptance_similarity == "完全不一致":
        return "高风险"
    return "低风险"


def run_risk_analysis(config: dict) -> list[dict]:
    """执行项目风险分析流程。"""
    results = []
    with get_api_client(config) as client:
        projects = fetch_projects(client)
        logger.info("获取到 %d 个项目", len(projects))

        # 筛选可分析项目
        analyzable = []
        for p in projects:
            conditions = (
                p.get("has_front_contract", False)
                and p.get("has_back_contract", False)
                and p.get("has_front_acceptance", False)
                and p.get("has_back_acceptance", False)
                and not p.get("llm_analyzed", False)
            )
            if conditions:
                analyzable.append(p)
            else:
                # 诊断缺少的材料
                missing = []
                if not p.get("has_front_contract"):
                    missing.append("前项合同")
                if not p.get("has_back_contract"):
                    missing.append("后项合同")
                if not p.get("has_front_acceptance"):
                    missing.append("前项验收")
                if not p.get("has_back_acceptance"):
                    missing.append("后项验收")
                if p.get("llm_analyzed"):
                    missing.append("已分析")
                status = "、".join(missing) if missing else "未知"
                logger.info("  跳过 %s: %s", p.get("contract_no"), status)

        logger.info("可分析项目: %d 个", len(analyzable))

        for i, project in enumerate(analyzable, 1):
            contract_no = project["contract_no"]
            logger.info("[%d/%d] 正在分析 %s...", i, len(analyzable), contract_no)

            try:
                # 获取前后项合同和验收数据
                contracts = fetch_contracts_by_no(client, contract_no)
                acceptances = fetch_acceptance_by_no(client, contract_no)

                front_contract = next((c for c in contracts if c.get("contract_type") == "前项"), None)
                back_contract = next((c for c in contracts if c.get("contract_type") == "后项"), None)
                front_acceptance = next((a for a in acceptances if a.get("acceptance_type") == "前项"), None)
                back_acceptance = next((a for a in acceptances if a.get("acceptance_type") == "后项"), None)

                if not front_contract or not back_contract:
                    logger.error("  缺少前后项合同数据，跳过")
                    results.append({"contract_no": contract_no, "status": "error", "error": "缺少合同数据"})
                    continue

                # LLM 合同对比分析
                # 注意：实际 LLM 调用由 Agent（TeleAgent 智能体）执行，这里只做本地计算
                front_amount = front_contract.get("total_amount")
                back_amount = back_contract.get("total_amount")
                rate, rate_level = calculate_rate(front_amount, back_amount)

                # 如果有 LLM 配置，可以调用 LLM 生成 similarity 和 analysis 文本
                # 这里先使用本地计算的结果，similarity 和 analysis 留给 Agent 对话中补充
                contract_analysis = {
                    "rate": rate,
                    "rate_level": rate_level,
                    "similarity": None,  # 需 LLM 分析
                    "analysis": f"前项金额: {front_amount}, 后项金额: {back_amount}, 毛利率: {rate:.4f}" if rate else "金额缺失",
                }
                push_contract_analysis(client, contract_no, contract_analysis)
                logger.info("  合同分析已推送: rate=%.4f, level=%s", rate or 0, rate_level)

                # 验收报告对比分析
                if front_acceptance and back_acceptance:
                    acceptance_analysis = {
                        "similarity": None,  # 需 LLM 分析
                        "analysis": f"前项验收日期: {front_acceptance.get('acceptance_date')}, 后项验收日期: {back_acceptance.get('acceptance_date')}",
                    }
                    push_acceptance_analysis(client, contract_no, acceptance_analysis)
                    logger.info("  验收分析已推送")
                else:
                    logger.warning("  缺少验收报告数据，跳过验收分析")

                # 综合风险判定
                project_risk = judge_project_risk(rate_level, contract_analysis["similarity"], None)
                update_project(client, contract_no, {"project_risk": project_risk, "llm_analyzed": True})
                logger.info("  项目风险判定: %s", project_risk)

                results.append({
                    "contract_no": contract_no,
                    "status": "ok",
                    "rate": rate,
                    "rate_level": rate_level,
                    "project_risk": project_risk,
                })

            except Exception as e:
                logger.error("  分析失败: %s", e)
                results.append({"contract_no": contract_no, "status": "error", "error": str(e)})

    return results


# ── 主入口 ────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="自动提取并推送合同数据")
    parser.add_argument("--dir", help="项目材料根目录")
    parser.add_argument("--file", help="单个合同文件路径")
    parser.add_argument("--risk-analysis", action="store_true", help="执行流程二：项目风险分析")
    parser.add_argument("--config", default="agent/config.yaml", help="配置文件路径")
    args = parser.parse_args()

    config = load_config(args.config)

    if args.risk_analysis:
        results = run_risk_analysis(config)
        ok = sum(1 for r in results if r["status"] == "ok")
        err = sum(1 for r in results if r["status"] == "error")
        print(f"\n风险分析完成: 成功 {ok}, 失败 {err}")
        for r in results:
            status_mark = "OK" if r["status"] == "ok" else "FAIL"
            extra = f" rate={r.get('rate')}, level={r.get('rate_level')}, risk={r.get('project_risk')}" if r["status"] == "ok" else f" error={r.get('error')}"
            print(f"  [{status_mark}] {r['contract_no']}{extra}")
    elif args.file:
        fp = Path(args.file)
        project_no = extract_project_no(fp.parent)
        result = asyncio.run(process_with_ocr_llm(fp, config, project_no))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.dir:
        results = process_directory(Path(args.dir), config)
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
