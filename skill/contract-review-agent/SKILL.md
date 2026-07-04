---
name: contract-review-agent
description: "Contract review agent for government-enterprise projects. Performs OCR text extraction, LLM structured field extraction, front/back contract classification, acceptance report parsing, and API push to the backend server. Use when the user mentions contract review, contract comparison, front-back contract analysis, contract OCR, contract data push, or batch processing of contract materials."
name_cn: 合同审查智能体
description_cn: 政企工程项目合同风控智能体，执行合同OCR识别、LLM结构化提取、前后项判定、验收报告解析，并推送至后端服务。适用于合同审查、前后项比对、批量合同材料处理等场景。
create_source: super-agent-skill-creator
---

# 合同审查智能体 (Contract Review Agent)

## Overview

本技能是政企工程项目合同风控系统的 **Agent 感知层**，负责将合同文件（PDF/docx/图片等）通过 OCR 提取文本，调用 LLM 结构化提取合同字段，自动判定前后项合同，并将结果推送到后端 API。同时支持验收报告的提取与推送。

触发场景：
- 用户提到"审查合同""比对合同""前后项合同""提取合同数据""合同OCR""推送合同""批量处理合同""验收报告提取"
- 用户指向合同材料目录（如 `A:\Inbox\contract\恒天项目材料\`）
- 用户要求启动比对、生成风险报告等后续操作

## Workflow Decision Tree

```
用户请求
├→ 单文件处理？→ 流程A: 单文件提取+推送
├→ 批量目录处理？→ 流程B: 批量扫描+自动配对+推送
├→ 已有提取数据？→ 流程C: 直接推送JSON
└→ 其他操作（比对/风险/报表）→ 提示用户先完成数据推送，或直接调用后端API
```

## 流程A: 单文件提取+推送

**适用场景**: 用户指向单个合同文件（PDF/docx/图片）

1. **OCR 提取文本**
   - 电子版 PDF → PyMuPDF / pdfplumber 直接提取文本层
   - 扫描件 PDF → pdf2image 转图片 → PaddleOCR 识别
   - docx → python-docx 提取
   - Excel → openpyxl 提取
   - 图片 → PaddleOCR 直接识别
   - 关键代码: `agent/ocr_extract.py` → `extract_text()`

2. **LLM 结构化提取**
   - 调用配置的 LLM（默认 qwen2.5-72b），提取合同字段
   - 提取字段: contract_no, party_a, party_b, signing_date, total_amount, amount_uppercase, payment_terms, delivery_terms, acceptance_terms, breach_terms, warranty_terms, line_items[]
   - JSON 解析兼容 markdown 代码块包裹
   - 关键代码: `agent/ocr_extract.py` → `llm_extract()`

3. **前后项判定**
   - 优先级: 文件名信号 → 合同编号匹配 → 默认前项
   - 前项信号: ["前项", "上家", "前"]
   - 后项信号: ["后项", "下家", "后"]
   - 关键代码: `agent/ocr_extract.py` → `judge_front_back()`

4. **推送到后端**
   - POST `/api/v1/contracts` (Agent API Key 认证)
   - 自动创建 Project（若 contract_no 不存在）
   - 同时推送 line_items 分项清单
   - 关键代码: `agent/ocr_extract.py` → `process_file()`

## 流程B: 批量目录处理

**适用场景**: 用户指向一个项目目录，包含多个子项目/城市的合同材料

1. **扫描目录**
   - 递归查找支持的文件类型: `.pdf, .docx, .doc, .xls, .xlsx, .jpg, .png`
   - 按子目录分组（通常按城市: 鹤岗/伊春/齐齐哈尔/哈尔滨）
   - 从目录名提取 project_no (如 `XYJAEXJCI250500015鹤岗` → `XYJAEXJCI250500015`)

2. **逐文件处理**
   - 对每个文件执行"流程A"的步骤1-4
   - 记录成功/失败状态，最后汇总

3. **目录结构约定**
   ```
   恒天项目材料/
   ├── XYJAEXJCI250500015鹤岗/
   │   └── 6.前后合同、验收报告/
   │       ├── 前项合同.pdf
   │       ├── 后项合同.pdf
   │       └── 验收报告.pdf
   ├── XYJAEXJCI250500016伊春/
   │   └── 6.前后合同、验收报告/
   │       ├── 前项合同_解析.json  (可能已有预提取数据)
   │       ├── 后项合同_解析.json
   │       └── ...
   ```

4. **预提取数据检测**
   - 部分目录（如伊春、哈尔滨）已有 `_解析.json` 文件
   - 检测到时走"流程C"直接推送，跳过 OCR + LLM

**关键脚本**: `scripts/auto_extract.py`

## 流程C: 直接推送JSON

**适用场景**: 已有预提取的 JSON 数据（如 `_解析.json` 文件）

1. **读取 JSON 文件**
   - 解析为 dict，映射到 ContractCreate schema
   - 注意字段名映射（JSON 可能用中文字段名）

2. **推送到后端**
   - 同流程A的步骤4

**关键脚本**: `scripts/push_contract.py`, `scripts/push_acceptance.py`

## 配置

Agent 使用 `agent/config.yaml` 配置文件:

```yaml
server:
  base_url: http://localhost:8000/api/v1
  api_key: change-me-to-a-random-agent-api-key

ocr:
  engine: paddleocr
  lang: ch

llm:
  base_url: https://api.example.com/v1
  api_key: your-llm-api-key
  model: qwen2.5-72b

signals:
  front: ["前项", "上家", "前"]
  back: ["后项", "下家", "后"]
```

**运行环境要求**:
- Python 3.12 (TeleAgent 内置运行时: `C:\Users\vanze\.local\share\TeleAgent\runtimes\python\python.exe`)
- 依赖: httpx, pyyaml, PyMuPDF, pdfplumber, pdf2image, paddleocr, python-docx, openpyxl
- 后端服务运行在 `http://localhost:8000`
- PostgreSQL 本地服务 (contract_review 数据库)
- MinIO / Redis Docker 容器运行中

## 后端 API 参考

### 合同 API
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/contracts` | X-API-Key | Agent 推送合同 |
| GET | `/api/v1/contracts` | - | 合同列表(分页) |
| GET | `/api/v1/contracts/{id}` | - | 合同详情(含分项) |
| PUT | `/api/v1/contracts/{id}` | JWT | 修正合同 |
| POST | `/api/v1/contracts/{id}/verify` | JWT | 人工确认 |
| DELETE | `/api/v1/contracts/{id}` | JWT | 删除合同 |

### 验收报告 API
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/acceptance` | X-API-Key | Agent 推送验收报告 |
| GET | `/api/v1/acceptance` | - | 验收列表(分页) |
| GET | `/api/v1/acceptance/{id}` | - | 验收详情 |
| PUT | `/api/v1/acceptance/{id}` | JWT | 修正验收报告 |
| POST | `/api/v1/acceptance/{id}/verify` | JWT | 人工确认 |

### 比对 API
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/comparisons/auto` | JWT | 自动配对比对 |
| GET | `/api/v1/comparisons` | - | 比对列表 |
| GET | `/api/v1/comparisons/{id}` | - | 比对详情(含分项) |

### 其他
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/dashboard/stats` | - | 仪表盘统计 |
| POST | `/api/v1/files/upload` | X-API-Key | 文件上传 MinIO |
| GET | `/api/v1/reports/{id}/export` | JWT | 导出 Excel 报表 |

### ContractCreate 必填字段
```json
{
  "contract_no": "XYJAEXJCI250500015",
  "contract_type": "前项|后项",
  "type_judge_basis": "文件名:xxx.pdf",
  "party_a": "甲方名称",
  "party_b": "乙方名称",
  "total_amount": 1000000.00,
  "signing_date": "2025-01-15",
  "amount_uppercase": "壹佰万元整",
  "payment_terms": "...",
  "delivery_terms": "...",
  "acceptance_terms": "...",
  "breach_terms": "...",
  "warranty_terms": "...",
  "source_file_name": "前项合同.pdf",
  "source_file_hash": "sha256...",
  "ocr_raw_text": "原始OCR文本...",
  "ocr_engine": "paddleocr",
  "llm_model": "qwen2.5-72b",
  "line_items": [
    {"item_no": 1, "item_name": "设备安装", "unit": "项", "quantity": 1, "unit_price": 500000, "amount": 500000}
  ]
}
```

### AcceptanceCreate 必填字段
```json
{
  "acceptance_no": "验收编号",
  "contract_no": "XYJAEXJCI250500015",
  "acceptance_type": "前项|后项",
  "type_judge_basis": "文件名:xxx.pdf",
  "acceptance_content": "验收内容摘要",
  "acceptance_date": "2025-06-30",
  "acceptance_result": "合格",
  "source_file_name": "验收报告.pdf",
  "source_file_hash": "sha256...",
  "ocr_raw_text": "原始OCR文本...",
  "ocr_engine": "paddleocr",
  "llm_model": "qwen2.5-72b"
}
```

## 注意事项

1. **OCR 依赖可选**: PaddleOCR 与 pdf2image 为可选依赖，未安装时自动降级（仅处理电子版文档）
2. **LLM 配置必须**: 结构化提取依赖 LLM API，需在 config.yaml 中配置有效的 base_url 和 api_key
3. **前后项判定**: 当前主要依赖文件名信号，后续可增加合同编号+金额规则判定
4. **幂等性**: 同一 source_file_hash 的文件重复推送会创建新记录（暂未做去重）
5. **大文件处理**: 超大 PDF（100+ 页）可能导致 OCR 超时，建议分批处理
6. **项目目录数据**: `A:\Inbox\contract\恒天项目材料\` 包含 4 个子项目约 479 个文件
7. **预提取数据**: 伊春和哈尔滨目录已有 `_解析.json`，可直接推送，无需重新 OCR/LLM

## Resources

### scripts/

- **auto_extract.py** - 主入口脚本，批量扫描目录并处理合同文件（智能检测预提取JSON或走OCR+LLM流程）
- **push_contract.py** - 读取已提取的 JSON 文件，推送到后端 `/api/v1/contracts`
- **push_acceptance.py** - 读取已提取的 JSON 文件，推送到后端 `/api/v1/acceptance`

### references/

- **api_reference.md** - 后端 API 完整参考文档
- **directory_guide.md** - 恒天项目材料目录结构与预提取数据说明
