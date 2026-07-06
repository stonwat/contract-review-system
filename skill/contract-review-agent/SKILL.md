---
name: contract-review-agent
description: "Contract review agent for government-enterprise projects. Performs OCR text extraction, LLM structured field extraction, front/back contract classification, acceptance report parsing, and API push to the backend server. Use when the user mentions contract review, contract comparison, front-back contract analysis, contract OCR, contract data push, or batch processing of contract materials."
name_cn: 合同审查智能体
description_cn: 政企工程项目合同风控智能体，执行合同OCR识别、LLM结构化提取、前后项判定、验收报告解析，并推送至后端服务。适用于合同审查、前后项比对、批量合同材料处理等场景。
create_source: super-agent-skill-creator
---

# 合同审查智能体 (Contract Review Agent)

## Overview

本技能是政企工程项目合同风控系统的 **数据入库层**，负责从用户提交的合同/验收文件到后端存储的完整流程。OCR 提取由 `paddleocr-doc-parsing` skill 完成，分析比对由 TeleAgent 用 LLM 完成，本 skill 覆盖从文件接收到数据推送的全链路。

触发场景：
- 用户在聊天中上传合同/验收报告文件（PDF/docx/图片）
- 用户指向合同材料目录（如 `A:\Inbox\contract\恒天项目材料\`）
- 用户提到"审查合同""推送合同""批量处理合同""验收报告入库"

## 完整工作流程

```
用户上传文件
     │
     ▼
 1. 规范化命名      命名规则: {合同编号}-{前项/后项}-{地市}.{ext}
     │
     ▼
 2. 去重检查        GET /contracts/check 或 /acceptance/check
     │               已存在 → 告知用户跳过
     ▼               不存在 → 继续
 3. 上传 MinIO      POST /files/upload → 拿到 object_key / file_hash
     │
     ▼
 4. OCR+LLM 提取    调用 paddleocr-doc-parsing skill
     │
     ▼
 5. 前后项判定      文件名信号 → 前项/后项
     │
     ▼
 6. 推送结构化数据  POST /contracts 或 /acceptance
```

## Workflow Decision Tree

```
用户请求
├→ 单个文件？→ 流程A: 命名→去重→上传MinIO→OCR+LLM→判定→推送
├→ 批量目录？→ 流程B: 逐文件扫描+自动配对+流程A 或 流程C
├→ 已有提取数据（JSON）？→ 流程C: 去重→推送（跳过OCR）
└→ 用户要求分析？→ 阶段二: TeleAgent 用 LLM 分析后推送分析结果
```

## 流程A: 单文件入库（主流程）

**适用场景**: 用户在聊天中上传单个合同/验收文件

1. **规范化命名**
   - 命名规则: `{合同编号}-{前项/后项}-{地市名称}.{ext}`
   - 示例: `XYJAEXJCI250500016-前项-伊春.pdf`
   - 合同编号需从文件内容或文件名推断；信息不足时先用临时命名

2. **去重检查**
   - 合同: `GET /api/v1/contracts/check?contract_no=XXX&contract_type=前项`
   - 验收: `GET /api/v1/acceptance/check?contract_no=XXX&acceptance_type=前项`
   - 已存在 → 告知用户"该合同已存在，跳过"，终止流程

3. **上传 MinIO**
   - `POST /api/v1/files/upload` 将原始文件上传到对象存储
   - 保存返回的 `object_key` 和 `file_hash`

4. **OCR + LLM 结构化提取**
   - 使用 `paddleocr-doc-parsing` skill 提取文档结构化数据
   - 合同字段: contract_no, party_a, party_b, signing_date, total_amount, amount_uppercase, payment_terms, delivery_terms, acceptance_terms, breach_terms, warranty_terms, line_items[]
   - 验收字段: acceptance_no, acceptance_date, acceptance_result, acceptance_content 等

5. **前后项判定**
   - 优先级: 文件名信号 → 合同编号匹配 → 默认前项
   - 前项信号: ["前项", "上家", "前"]
   - 后项信号: ["后项", "下家", "后"]

6. **推送到后端**
   - 合同: `POST /api/v1/contracts` (X-API-Key 认证)
   - 验收: `POST /api/v1/acceptance` (X-API-Key 认证)
   - 后端自动创建 Project（若 contract_no 不存在）+ 维护 has_* 标记

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

## 阶段二: Agent 分析（TeleAgent 用 LLM 完成）

**适用场景**: 项目四份材料入库后，用户要求分析/比对/审查

1. **合同对比分析**
   - 拉取项目前后项合同: `GET /api/v1/contracts?contract_no=XXX`
   - 用 LLM 对比前后项合同的条款（付款/交付/验收/违约/质保等）
   - 计算毛利率: `(前项金额 - 后项金额) / 前项金额`
   - 判定等级: <0 利润倒挂 / <0.05 低毛利 / >=0.05 正常
   - 判定一致性: 完全一致 / 有一致性风险 / 完全不一致
   - 推送结果: `POST /api/v1/contract-analysis` (UPSERT)

2. **验收对比分析**
   - 拉取前后项验收报告: `GET /api/v1/acceptance?contract_no=XXX`
   - 用 LLM 对比前后项验收报告的一致性
   - 推送结果: `POST /api/v1/acceptance-analysis` (UPSERT)

3. **综合风险判定**
   - 结合毛利率、一致性、条款风险等综合判定项目风险等级
   - 更新项目: `PUT /api/v1/projects/{contract_no}` → `project_risk` + `llm_analyzed=true`

4. **告知用户**
   - 汇报分析结果：毛利率、一致性、风险等级

## 运行环境要求
- Python 3.12 (TeleAgent 内置运行时: `C:\Users\vanze\.local\share\TeleAgent\runtimes\python\python.exe`)
- 依赖: httpx, pyyaml
- OCR 提取依赖 `paddleocr-doc-parsing` skill
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

### 文件与项目 API
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/files/upload` | CurrentAdmin | 文件上传 MinIO |
| GET | `/api/v1/contracts/check` | CurrentAdmin | 合同去重检查 |
| GET | `/api/v1/acceptance/check` | CurrentAdmin | 验收报告去重检查 |
| GET | `/api/v1/contracts/cards` | CurrentAdmin | 项目卡片列表(前后项并排) |
| GET | `/api/v1/projects` | CurrentAdmin | 项目列表 |
| PUT | `/api/v1/projects/{contract_no}` | CurrentAdmin | 更新项目(风险等级/审查状态) |

### 分析 API
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/contract-analysis` | X-API-Key | Agent 推送合同分析结果(UPSERT) |
| GET | `/api/v1/contract-analysis/{contract_no}` | CurrentAdmin | 查询合同分析结果 |
| POST | `/api/v1/contract-analysis/{contract_no}/verify` | CurrentAdmin | 确认合同分析 |
| POST | `/api/v1/acceptance-analysis` | X-API-Key | Agent 推送验收分析结果(UPSERT) |
| GET | `/api/v1/acceptance-analysis/{contract_no}` | CurrentAdmin | 查询验收分析结果 |
| POST | `/api/v1/acceptance-analysis/{contract_no}/verify` | CurrentAdmin | 确认验收分析 |

### 报表与仪表盘
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/dashboard/overview` | CurrentAdmin | 仪表盘总览 |
| GET | `/api/v1/dashboard/city-stats` | CurrentAdmin | 按地市统计 |
| GET | `/api/v1/reports/contract-consistency` | CurrentAdmin | 合同一致性报表 |
| GET | `/api/v1/reports/acceptance-consistency` | CurrentAdmin | 验收一致性报表 |
| GET | `/api/v1/reports/low-margin` | CurrentAdmin | 低毛利项目报表 |
| GET | `/api/v1/reports/high-risk` | CurrentAdmin | 高风险项目报表 |
| GET | `/api/v1/reports/export` | CurrentAdmin | 导出 Excel |

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

1. **去重必须先做**: 推送前必须先调用 `/contracts/check` 或 `/acceptance/check`，避免重复入库
2. **MinIO 上传在 OCR 之前**: 文件先存 MinIO，再 OCR 提取，保证原始文件有存档
3. **OCR 由 paddleocr-doc-parsing skill 完成**: 本 skill 不内置 OCR/LLM 逻辑
4. **分析由 TeleAgent 直接用 LLM 完成**: 后端不负责分析计算，只负责存储和查询
5. **前后项判定**: 主要依赖文件名信号，后续可增加合同编号+金额规则判定

## Resources

### scripts/

- **auto_extract.py** - 主入口脚本，批量扫描目录并处理合同文件（智能检测预提取JSON或走OCR+LLM流程）
- **push_contract.py** - 读取已提取的 JSON 文件，推送到后端 `/api/v1/contracts`
- **push_acceptance.py** - 读取已提取的 JSON 文件，推送到后端 `/api/v1/acceptance`

### references/

- **api_reference.md** - 后端 API 完整参考文档
- **directory_guide.md** - 恒天项目材料目录结构与预提取数据说明
