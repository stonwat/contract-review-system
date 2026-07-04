"""OCR + LLM 结构化提取 → 推送服务端 API。

处理单个文件的完整流程：
  1. 文件类型判断与文本提取（OCR / 直读）
  2. LLM 结构化提取合同字段
  3. 前后项判定（合同编号匹配 + 文件名信号）
  4. POST /contracts 推送到服务端
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
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
    """根据文件类型提取文本。

    优先级：
    1. 电子版 PDF/docx → 直接提取文本层
    2. 扫描件 PDF / 图片 → PaddleOCR 识别
    """
    ext = file_path.suffix.lower()

    if ext == ".pdf":
        text = _extract_pdf_text(file_path)
        if text.strip():
            return text
        # 文本层为空，尝试 OCR
        return _ocr_pdf(file_path)

    if ext in {".docx", ".doc"}:
        return _extract_docx_text(file_path)

    if ext in {".jpg", ".jpeg", ".png"}:
        return _ocr_image(file_path)

    if ext in {".xls", ".xlsx"}:
        return _extract_excel_text(file_path)

    logger.warning("不支持的文件类型: %s", ext)
    return ""


def _extract_pdf_text(file_path: Path) -> str:
    """提取电子版 PDF 文本层。"""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(file_path))
        pages = []
        for page in doc:
            pages.append(page.get_text())
        doc.close()
        return "\n".join(pages)
    except ImportError:
        logger.warning("PyMuPDF 未安装，尝试 pdfplumber")
    except Exception as e:
        logger.warning("PyMuPDF 提取失败: %s", e)

    try:
        import pdfplumber
        pages = []
        with pdfplumber.open(str(file_path)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        return "\n".join(pages)
    except ImportError:
        logger.warning("pdfplumber 也未安装，PDF 文本提取跳过")
    except Exception as e:
        logger.warning("pdfplumber 提取失败: %s", e)

    return ""


def _ocr_pdf(file_path: Path) -> str:
    """PaddleOCR 识别 PDF 扫描件。先转图片再 OCR。"""
    try:
        from pdf2image import convert_from_path
        from paddleocr import PaddleOCR

        ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
        images = convert_from_path(str(file_path))
        pages = []
        for img in images:
            result = ocr.ocr(img, cls=True)
            lines = []
            if result and result[0]:
                for line in result[0]:
                    lines.append(line[1][0])
            pages.append("\n".join(lines))
        return "\n".join(pages)
    except ImportError as e:
        logger.warning("PDF OCR 依赖缺失 (%s)，跳过扫描件识别", e)
    except Exception as e:
        logger.warning("PDF OCR 失败: %s", e)
    return ""


def _ocr_image(file_path: Path) -> str:
    """PaddleOCR 识别图片。"""
    try:
        from paddleocr import PaddleOCR

        ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
        result = ocr.ocr(str(file_path), cls=True)
        if result and result[0]:
            return "\n".join(line[1][0] for line in result[0])
    except ImportError as e:
        logger.warning("PaddleOCR 未安装 (%s)", e)
    except Exception as e:
        logger.warning("图片 OCR 失败: %s", e)
    return ""


def _extract_docx_text(file_path: Path) -> str:
    """提取 docx 文件文本。"""
    try:
        from docx import Document
        doc = Document(str(file_path))
        return "\n".join(para.text for para in doc.paragraphs if para.text.strip())
    except ImportError:
        logger.warning("python-docx 未安装，跳过 docx 提取")
    except Exception as e:
        logger.warning("docx 提取失败: %s", e)
    return ""


def _extract_excel_text(file_path: Path) -> str:
    """提取 Excel 文本内容。"""
    try:
        from openpyxl import load_workbook
        wb = load_workbook(str(file_path), read_only=True)
        rows = []
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                cells = [str(c) for c in row if c is not None]
                if cells:
                    rows.append("\t".join(cells))
        wb.close()
        return "\n".join(rows)
    except ImportError:
        logger.warning("openpyxl 未安装，跳过 Excel 提取")
    except Exception as e:
        logger.warning("Excel 提取失败: %s", e)
    return ""


def _parse_json_response(text: str) -> dict[str, Any]:
    """从 LLM 响应中解析 JSON，兼容 markdown 代码块包裹。"""
    # 尝试提取 ```json ... ``` 块
    m = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    json_str = m.group(1) if m else text

    # 去除首尾非 JSON 字符
    json_str = json_str.strip()
    start = json_str.find("{")
    end = json_str.rfind("}")
    if start >= 0 and end > start:
        json_str = json_str[start : end + 1]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning("JSON 解析失败: %s, 原文: %s", e, text[:200])
        return {}


async def llm_extract(text: str, config: AgentConfig) -> dict[str, Any]:
    """调用 LLM 提取合同结构化字段，返回解析后的 dict。"""
    if not text:
        return {}
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{config.llm_base_url}/chat/completions",
            headers={"Authorization": f"Bearer {config.llm_api_key}"},
            json={
                "model": config.llm_model,
                "messages": [
                    {"role": "system", "content": "你是合同信息提取助手，只输出 JSON，不要输出其他内容。"},
                    {"role": "user", "content": f"{CONTRACT_SCHEMA_HINT}\n\n合同文本：\n{text}"},
                ],
            },
        )
        resp.raise_for_status()
        raw_content = resp.json()["choices"][0]["message"]["content"]
        parsed = _parse_json_response(raw_content)
        if parsed:
            return parsed
        # 解析失败时返回原始文本
        return {"raw": raw_content}


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
