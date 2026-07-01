"""OCR + LLM 结构化提取 → 推送服务端 API。

处理单个文件的完整流程：
  1. 文件类型判断与文本提取（OCR / 直读）
  2. LLM 结构化提取合同字段
  3. 前后项判定（合同编号匹配 + 文件名信号）
  4. POST /contracts 推送到服务端
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any

import httpx

from agent.config_client import AgentConfig, make_client

logger = logging.getLogger(__name__)

# 合同字段提取的 JSON Schema 提示
CONTRACT_SCHEMA_HINT = """请从合同文本中提取以下字段，输出 JSON：
{
  "contract_no": "合同编号",
  "party_a": "甲方",
  "party_b": "乙方",
  "signing_date": "YYYY-MM-DD",
  "total_amount": 数字,
  "amount_uppercase": "大写金额",
  "payment_terms": "付款条款原文",
  "delivery_terms": "交付条款原文",
  "acceptance_terms": "验收条款原文",
  "breach_terms": "违约责任原文",
  "warranty_terms": "质保条款原文",
  "line_items": [{"item_no": 1, "item_name": "...", "unit": "...", "quantity": 1, "unit_price": 0, "amount": 0}]
}
缺失字段用 null 表示。"""


def extract_text(file_path: Path) -> str:
    """根据文件类型提取文本。骨架：仅处理电子版 PDF/docx，扫描件需接 PaddleOCR。"""
    ext = file_path.suffix.lower()
    if ext in {".pdf", ".docx", ".doc", ".xls", ".xlsx"}:
        # 实际项目：
        #   扫描件 PDF / 图片 → PaddleOCR 识别
        #   电子版 PDF / docx → 直接提取文本层
        # 此处骨架返回占位，由实际 OCR 实现填充
        logger.info("提取文本: %s (扩展名 %s)", file_path.name, ext)
        return ""
    logger.warning("不支持的文件类型: %s", ext)
    return ""


async def llm_extract(text: str, config: AgentConfig) -> dict[str, Any]:
    """调用 LLM 提取合同结构化字段。"""
    if not text:
        return {}
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{config.llm_base_url}/chat/completions",
            headers={"Authorization": f"Bearer {config.llm_api_key}"},
            json={
                "model": config.llm_model,
                "messages": [
                    {"role": "system", "content": "你是合同信息提取助手，只输出 JSON。"},
                    {"role": "user", "content": f"{CONTRACT_SCHEMA_HINT}\n\n合同文本：\n{text}"},
                ],
            },
        )
        resp.raise_for_status()
        # 实际项目应解析 JSON 并容错，此处返回原始内容
        return {"raw": resp.json()["choices"][0]["message"]["content"]}


def judge_front_back(filename: str, config: AgentConfig, contract_no: str) -> str:
    """前后项判定。优先级：合同编号匹配 → 文件名信号。返回 '前项' 或 '后项'。"""
    name = filename
    if any(sig in name for sig in config.front_signals):
        return "前项"
    if any(sig in name for sig in config.back_signals):
        return "后项"
    # 无法从文件名判定时，依赖服务端已有的同 contract_no 记录
    logger.warning("无法从文件名判定前后项，contract_no=%s，默认前项", contract_no)
    return "前项"


def file_hash(file_path: Path) -> str:
    """计算文件 SHA256。"""
    h = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


async def process_file(file_path: Path, config: AgentConfig) -> dict[str, Any]:
    """处理单个合同文件，推送到服务端。"""
    text = extract_text(file_path)
    extracted = await llm_extract(text, config)
    contract_no = extracted.get("contract_no", file_path.stem)
    contract_type = judge_front_back(file_path.name, config, str(contract_no))

    payload = {
        "contract_no": str(contract_no),
        "contract_type": contract_type,
        "type_judge_basis": f"文件名:{file_path.name}",
        "source_file_name": file_path.name,
        "source_file_hash": file_hash(file_path),
        "ocr_raw_text": text,
        "ocr_engine": "paddleocr",
        "llm_model": config.llm_model,
        **{k: v for k, v in extracted.items() if k != "raw"},
    }

    with make_client(config) as client:
        resp = client.post("/contracts", json=payload)
        resp.raise_for_status()
        return resp.json()
