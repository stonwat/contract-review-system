---
name: contract-review-agent
description: "Contract review agent for government-enterprise projects. Receives contract files from chat, renames and uploads to MinIO, performs OCR+LLM extraction, checks duplicates, and pushes structured data to backend. Supports front/back contract classification and automatic gross margin calculation. Use when user uploads contract files or mentions contract review, contract extraction, or acceptance report parsing."
name_cn: 合同审查智能体
description_cn: 政企工程项目合同风控智能体，通过聊天窗口接收合同文件，执行文件命名、MinIO上传、OCR+LLM提取、去重检查、结构化推送。支持前后项判定和毛利率自动计算。适用于合同审查、合同提取、验收报告解析等场景。
create_source: super-agent-skill-creator
---

# 合同审查智能体 (Contract Review Agent)

## Overview

本技能是政企工程项目合同风控系统的 **Agent 感知层**，通过聊天窗口接收用户提交的合同文件，执行以下流程：

1. **文件重命名** — 按规范命名: `{合同编号}-{前项/后项}-{地市名称}.{ext}`
2. **MinIO 上传** — 将原始文件上传至对象存储
3. **OCR + LLM 提取** — 提取合同结构化字段
4. **去重检查** — 调用 `GET /contracts/check` 确认不重复
5. **推送后端** — `POST /contracts` 或 `POST /acceptance`
6. **自动毛利率计算** — 后项合同插入时，后端自动计算毛利率并写入 Project

触发场景：
- 用户在聊天中上传合同文件（PDF/docx/图片）
- 用户提到"审查合同""提取合同""前后项合同""合同OCR""推送合同"
- 用户指向合同材料目录请求批量处理
- 用户要求处理验收报告

## Workflow Decision Tree

```
用户提交文件
├→ 单文件处理？→ 流程A: 聊天窗口→命名→上传→提取→去重→推送
├→ 批量目录处理？→ 流程B: 逐文件扫描+自动配对+推送
├→ 已有提取数据？→ 流程C: 直接推送JSON
└→ 验收报告？→ 流程D: 验收报告提取+推送
```

## 流程A: 聊天窗口单文件处理（主流程）

**适用场景**: 用户通过聊天窗口上传单个合同文件

1. **接收文件**
   - 用户在聊天中上传文件（PDF/docx/图片/Excel）
   - 记录原始文件名和大小

2. **文件重命名**
   - 命名规范: `{合同编号}-{前项/后项}-{地市名称}.{ext}`
   - 示例: `XYJAEXJCI250500016-前项-伊春.pdf`
   - 需要先进行 LLM 提取或从文件名推测合同编号和类型
   - 若信息不完整，使用临时命名，推送后由后端记录原始文件名

3. **MinIO 上传**
   - 调用 `POST /api/v1/files/upload` 上传原始文件
   - 保存返回的 file_id (MinIO object key)

4. **OCR 提取文本**
   - 电子版 PDF → PyMuPDF / pdfplumber 直接提取文本层
   - 扫描件 PDF → pdf2image 转图片 → PaddleOCR 识别
   - docx → python-docx 提取
   - Excel → openpyxl 提取
   - 图片 → PaddleOCR 直接识别

5. **LLM 结构化提取**
   - 调用配置的 LLM（默认 qwen2.5-72b），提取合同字段
   - 提取字段: contract_no, party_a, party_b, signing_date, total_amount, amount_uppercase, payment_terms, delivery_terms, acceptance_terms, breach_terms, warranty_terms, line_items[]
   - JSON 解析兼容 markdown 代码块包裹

6. **前后项判定**
   - 优先级: 文件名信号 → 合同编号匹配 → 默认前项
   - 前项信号: ["前项", "上家", "前"]
   - 后项信号: ["后项", "下家", "后"]

7. **去重检查**
   - `GET /api/v1/contracts/check?contract_no=XXX&contract_type=前项`
   - 若已存在，告知用户"该合同已存在，跳过"并返回已有记录ID

8. **推送后端**
   - `POST /api/v1/contracts` (Agent API Key 认证)
   - 自动创建 Project（若 contract_no 不存在）
   - 同时推送 line_items 分项清单
   - **后项合同插入后，后端自动计算毛利率**并写入 Project.gross_margin_rate 和 gross_margin_level

9. **告知用户结果**
   - 提示: 合同已入库、毛利率已计算、项目状态等

## 流程B: 批量目录处理

**适用场景**: 用户指向一个项目目录，包含多个子项目/城市的合同材料

1. **扫描目录**
   - 递归查找支持的文件类型: `.pdf, .docx, .doc, .xls, .xlsx, .jpg, .png`
   - 按子目录分组（通常按城市）
   - 从目录名提取 contract_no

2. **逐文件处理**
   - 对每个文件执行"流程A"的完整流程
   - 记录成功/失败状态，最后汇总

3. **目录结构约定**
   ```
   恒天项目材料/
   ├── XYJAEXJCI250500015鹤岗/
   │   └── 6.前后合同、验收报告/
   │       ├── 前项合同.pdf
   │       ├── 后项合同.pdf
   │       └── 验收报告.pdf
   ```

4. **预提取数据检测**
   - 部分目录（如伊春、哈尔滨）已有 `*关键信息提取.json` 文件
   - 检测到时走"流程C"直接推送，跳过 OCR + LLM

**关键脚本**: `scripts/auto_extract.py`

## 流程C: 直接推送JSON

**适用场景**: 已有预提取的 JSON 数据（如 `*关键信息提取.json` 文件）

1. **去重检查** — 先调用 check API
2. **读取 JSON 文件** — 解析为 dict，映射到 ContractCreate schema
3. **推送后端** — `POST /api/v1/contracts`

**关键脚本**: `scripts/push_contract.py`, `scripts/push_acceptance.py`

## 流程D: 验收报告处理

1. **OCR + LLM 提取** — 提取验收编号、验收日期、验收结果等
2. **推送** — `POST /api/v1/acceptance`

## 毛利率自动计算逻辑

当 **后项合同** 成功推送后，后端自动执行：

1. 查找同一 contract_no 的前项和后项合同
2. 计算毛利率: `margin_rate = (front_amount - back_amount) / front_amount`
3. 判定等级:
   - `margin_rate < 0` → **利润倒挂**
   - `margin_rate < 0.05` → **低毛利**
   - `margin_rate >= 0.05` → **正常**
4. 写入 Project 表的 `gross_margin_rate` 和 `gross_margin_level` 字段

前端以卡片布局展示，左右并排显示前后项合同信息，底部显示毛利率和确认状态。

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
| GET | `/api/v1/contracts/check` | - | 去重检查(contract_no + contract_type) |
| GET | `/api/v1/contracts/cards` | - | 项目卡片列表(前后项并排) |
| POST | `/api/v1/contracts` | X-API-Key | Agent 推送合同(后项自动算毛利率) |
| GET | `/api/v1/contracts` | - | 合同列表(分页) |
| GET | `/api/v1/contracts/{id}` | - | 合同详情(含分项) |
| PUT | `/api/v1/contracts/{id}` | JWT | 修正合同(金额变更自动重算毛利率) |
| POST | `/api/v1/contracts/{id}/verify` | JWT | 人工确认 |
| DELETE | `/api/v1/contracts/{id}` | JWT | 删除合同(删除后重算毛利率) |

### 验收报告 API
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/acceptance` | X-API-Key | Agent 推送验收报告 |
| GET | `/api/v1/acceptance` | - | 验收列表(分页) |
| GET | `/api/v1/acceptance/{id}` | - | 验收详情 |
| PUT | `/api/v1/acceptance/{id}` | JWT | 修正验收报告 |
| POST | `/api/v1/acceptance/{id}/verify` | JWT | 人工确认 |

### 仪表盘 API
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/dashboard/overview` | - | 总览(项目数/合同数/配对数/毛利率异常) |
| GET | `/api/v1/dashboard/city-stats` | - | 按地市统计 |

### 报表 API
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/reports/contracts` | JWT | 合同报表(按项目汇总) |
| GET | `/api/v1/reports/margin` | JWT | 毛利率报表(低毛利+利润倒挂) |
| GET | `/api/v1/reports/acceptance` | JWT | 验收报告汇总 |
| GET | `/api/v1/reports/export` | JWT | 导出 Excel |

### 其他
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/files/upload` | X-API-Key | 文件上传 MinIO |

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
  "source_file_name": "XYJAEXJCI250500015-前项-鹤岗.pdf",
  "source_file_hash": "sha256...",
  "ocr_raw_text": "原始OCR文本...",
  "ocr_engine": "paddleocr",
  "llm_model": "qwen2.5-72b",
  "line_items": [
    {"item_no": 1, "item_name": "设备安装", "unit": "项", "quantity": 1, "unit_price": 500000, "amount": 500000}
  ]
}
```

## 注意事项

1. **去重检查**: 推送前必须先调用 `/contracts/check` 确认不重复
2. **文件命名**: 按规范 `{合同编号}-{前项/后项}-{地市名称}.{ext}` 重命名后上传 MinIO
3. **毛利率自动计算**: 后项合同推送后，后端自动计算；无需前端/Agent 手动计算
4. **LLM 配置必须**: 结构化提取依赖 LLM API，需在 config.yaml 中配置有效凭证
5. **前后项判定**: 当前主要依赖文件名信号，后续可增加合同编号+金额规则判定
6. **大文件处理**: 超大 PDF（100+ 页）可能导致 OCR 超时，建议分批处理
7. **项目目录数据**: `A:\Inbox\contract\恒天项目材料\` 包含 4 个子项目

## Resources

### scripts/

- **auto_extract.py** - 主入口脚本，批量扫描目录并处理合同文件
- **push_contract.py** - 读取已提取的 JSON 文件，推送到后端
- **push_acceptance.py** - 读取已提取的 JSON 文件，推送到后端

### references/

- **api_reference.md** - 后端 API 完整参考文档
- **directory_guide.md** - 恒天项目材料目录结构与预提取数据说明
