---
name: contract-review-agent
description: "Contract review agent for government-enterprise projects. Receives contract/acceptance files via chat, renames and uploads to MinIO, performs LLM extraction, checks duplicates, pushes structured data to backend. Supports two workflows: document submission and project risk analysis. Use when user uploads contract files or mentions contract review, contract extraction, acceptance report parsing, or risk analysis."
name_cn: 合同审查智能体
description_cn: 政企工程项目合同风控智能体。通过聊天窗口接收合同/验收报告文件，执行文件命名、MinIO上传、LLM提取、查重、结构化推送。支持两大流程：文档提交和项目风险分析。适用于合同审查、合同提取、验收报告解析、风险分析等场景。
create_source: super-agent-skill-creator
---

# 合同审查智能体 (Contract Review Agent)

## Overview

本技能是政企工程项目合同风控系统的 **Agent 感知与分析层**，通过聊天窗口与用户交互，执行两大核心流程：

- **流程一：文档提交** — 用户提交合同/验收报告文件 → Agent 读取→命名校验→类型判断→MinIO上传→查重→LLM提取→推送→自动维护 has_* 标记
- **流程二：项目风险分析** — 用户指令触发 → Agent 检查四布尔条件 → LLM 合同对比+验收对比+综合风险判定 → 回写 projects

触发场景：
- 用户在聊天中上传合同/验收报告文件（PDF/docx/图片）
- 用户提到"审查合同""提取合同""前后项合同""合同OCR""推送合同"
- 用户指向合同材料目录请求批量处理
- 用户要求"风险分析""分析项目风险""跑一下分析"
- 用户要求重新分析某个项目

## 系统架构

```
用户 ←→ Agent（本技能）←→ Server（FastAPI + PostgreSQL）
                            ↑                    ↑
                         API 调用            MinIO 文件存储
```

| 层级 | 组件 | 职责 |
|:---|:---|:---|
| 感知与分析层 | 本地 Agent（本技能） | 文档接收、命名校验、查重、MinIO上传、LLM提取、数据推送、LLM对比分析、综合风险判定 |
| 存储层 | Server（FastAPI + PostgreSQL） | 数据存储、材料完整性标记维护（has_*）、API服务 |
| 展示层 | Frontend（Vue3 + Element Plus） | 卡片展示、人工确认、分析结果查看、项目审查管理 |

---

## 流程一：文档提交

### 1.1 总体流程

```
用户提交文件（合同 / 验收报告）
    │
    ▼
Step 1. 读取分析文档内容
    │
    ▼
Step 2. 校验文件名规范
   规范格式：项目名称-合同编号-上传人员.扩展名
   ├── 规范 → 直接使用
   └── 不规范 → Agent 生成规范名称，询问用户确认
    │
    ▼
Step 3. 判断文档类型
   ├── 无法判断 → 询问用户"这是合同还是验收报告？"
   ├── 合同 → 走流程 A
   └── 验收报告 → 走流程 B
    │
    ▼
Step 4. 归档文件
   使用规范文件名上传 MinIO，获取 object_key
```

### 1.2 文件命名规范

**格式**：`项目名称-合同编号-上传人员.扩展名`

| 组成部分 | 来源 | 规则 | 示例 |
|:---|:---|:---|:---|
| 项目名称 | 文档内容识别 | 保留原始项目全称 | 黑龙江省（伊春）传输管线工程施工服务项目 |
| 合同编号 | 文档内容识别 | 提取正式的合同号 | XYJAEXJCI250500016 |
| 上传人员 | 用户指定或默认登录用户 | 用户对话中指定，未指定则取当前登录用户名 | 张三 / admin |
| 扩展名 | 保留原始格式 | .pdf / .jpg / .docx | .pdf |

**命名处理步骤**：

```
1. 读取原始文件名
2. 正则匹配是否已符合 "项目名称-合同编号-上传人员.扩展名" 格式
   ├── 匹配 → 直接使用
   └── 不匹配 →
       ├── 从文档内容提取项目名称、合同编号
       ├── 询问用户："请指定上传人员（不指定则默认 [登录用户]）"
       │   ├── 用户输入 → 使用用户输入
       │   └── 用户不输入 → 使用登录用户名
       └── 生成规范文件名 →
           "黑龙江省（伊春）传输管线工程施工服务项目-XYJAEXJCI250500016-张三.pdf"
           并询问用户确认
```

### 1.3 文档类型判断

| 文档内容特征 | 判断结果 |
|:---|:---|
| 包含"合同"、"甲方"、"乙方"、"签约"、"总金额"等关键词 | 合同 |
| 包含"验收报告"、"验收日期"、"验收结果"、"验收结论"等关键词 | 验收报告 |
| 两者特征都不明显 | 询问用户 |

### 1.4 流程 A：合同提交

```
Step A1. 查重
   调用 GET /api/v1/contracts/check?contract_no=XXX&contract_type=前项
   ├── 已存在 → 提示用户"该合同已存在"，终止流程
   └── 不存在 → 继续

Step A2. LLM 结构化提取
   发送合同文档给 LLM，按 contracts 表字段提取 JSON
   ├── 提取成功 → 解析 JSON，继续
   └── 提取失败 → 提示用户"文档内容无法识别"，终止流程

Step A3. 推送到服务器
   POST /api/v1/contracts
   字段：所有提取的合同字段 + source_file_name
   后端自动处理：
   ├── 写入 contracts 表
   └── 更新 projects 表布尔标记
       ├── contract_type="前项" → has_front_contract = true
       └── contract_type="后项" → has_back_contract = true

Step A4. 反馈给用户
   "合同已提交：项目 [项目名称]，合同编号 [contract_no]，[contract_type]"
```

### 1.5 流程 B：验收报告提交

```
Step B1. 查重
   调用 GET /api/v1/acceptance/check?contract_no=XXX&acceptance_type=前项
   ├── 已存在 → 提示用户，终止流程
   └── 不存在 → 继续

Step B2. LLM 结构化提取
   按 acceptance_reports 表字段提取 JSON

Step B3. 推送到服务器
   POST /api/v1/acceptance
   后端自动更新 projects 表布尔标记：
   ├── acceptance_type="前项" → has_front_acceptance = true
   └── acceptance_type="后项" → has_back_acceptance = true

Step B4. 反馈给用户
```

---

## 流程二：项目风险分析

### 2.1 触发方式

用户在对话中发出明确指令：
- "进行项目风险分析"
- "分析一下这个项目的风险"
- "跑一下风险分析"

> **不自动触发**。即使项目材料齐全，也需用户明确指令才执行分析。

### 2.2 分析流程

```
用户发出风险分析指令
    │
    ▼
Step 1. 获取全部项目列表
   GET /api/v1/projects
    │
    ▼
Step 2. 逐项目检查触发条件
   筛选条件：
   has_front_contract   = true
   has_back_contract    = true
   has_front_acceptance = true
   has_back_acceptance  = true
   llm_analyzed         = false

   ├── 无项目满足 → 反馈用户（列出缺少的材料或已分析的项目）
   └── 有满足条件的项目 → 逐个处理
    │
    ▼
Step 3. 获取前后项合同和验收数据
   GET /api/v1/contracts?contract_no=XXX
   GET /api/v1/acceptance?contract_no=XXX
    │
    ▼
Step 4. LLM 合同对比分析
   ├── 计算毛利率：(前项金额 - 后项金额) / 前项金额
   ├── 判定等级：利润倒挂(<0) / 低毛利(<5%) / 正常(>=5%)
   ├── 分析条款一致性：完全一致 / 有一致性风险 / 完全不一致
   └── 生成分析文本
   → POST /api/v1/contract-analysis（UPSERT）
    │
    ▼
Step 5. LLM 验收报告对比分析
   ├── 分析内容一致性
   └── 生成分析文本
   → POST /api/v1/acceptance-analysis（UPSERT）
    │
    ▼
Step 6. LLM 综合判定项目风险
   ├── 高风险：利润倒挂 / 低毛利 / 任一 similarity="完全不一致"
   └── 低风险：以上条件均不满足
   → PUT /api/v1/projects/{contract_no}
     Body: {"project_risk": "低风险/高风险", "llm_analyzed": true}
    │
    ▼
Step 7. 向用户反馈分析结果汇总
```

### 2.3 毛利率判定规则

| 条件 | 等级 |
|:---|:---|
| rate < 0 | 利润倒挂 |
| 0 <= rate < 0.05 | 低毛利 |
| rate >= 0.05 | 正常 |

### 2.4 项目风险判定规则

| 条件 | 风险等级 |
|:---|:---|
| 利润倒挂 | 高风险 |
| 低毛利 | 高风险 |
| 任一 similarity 为"完全不一致" | 高风险 |
| 以上条件均不满足 | 低风险 |

### 2.5 重新分析

用户可请求重新分析：
```
PUT /api/v1/projects/{contract_no}
Body: {"llm_analyzed": false}
```
然后重新执行 Step 3 ~ Step 7。分析表中的 verified 字段会被重置为 false。

---

## LLM Prompt 模板

### 合同提取 Prompt

```
你是一个合同信息提取助手。请从以下合同文档中提取结构化信息，返回 JSON 格式。

【文档类型】合同
【文档内容】
{文档全文文本}

请提取以下字段并按 JSON 格式返回：

{
  "project_name": "项目名称（完整项目全称）",
  "city": "地市名称",
  "contract_no": "合同编号",
  "contract_type": "前项/后项",
  "type_judge_basis": "判定依据",
  "party_a": "甲方名称",
  "party_b": "乙方名称",
  "our_role": "我方角色（甲方/乙方）",
  "signing_date": "签约日期（YYYY-MM-DD）",
  "contract_period": "工期描述",
  "total_amount": "合同总金额（数字，单位元）",
  "amount_uppercase": "大写金额",
  "tax_rate": "税率（如0.09表示9%）",
  "payment_terms": "付款条款",
  "delivery_terms": "交付条款",
  "acceptance_terms": "验收条款",
  "breach_terms": "违约责任",
  "warranty_terms": "质保条款",
  "ip_terms": "知识产权条款",
  "other_key_terms": "其他关键条款"
}

注意：
- 缺失的字段用 null
- 金额只返回数字，不包含单位
- 日期格式统一为 YYYY-MM-DD
```

### 验收报告提取 Prompt

```
你是一个验收报告信息提取助手。请从以下验收报告文档中提取结构化信息，返回 JSON 格式。

【文档类型】验收报告
【文档内容】
{文档全文文本}

请提取以下字段并按 JSON 格式返回：

{
  "acceptance_no": "验收编号",
  "contract_no": "合同编号",
  "acceptance_type": "前项/后项",
  "type_judge_basis": "判定依据",
  "acceptance_content": "验收通过的工程内容描述",
  "acceptance_date": "验收日期（YYYY-MM-DD）",
  "acceptance_result": "验收结果"
}
```

### 合同对比分析 Prompt

```
你是一个合同对比分析专家。请对比同一个项目的前项和后项合同，返回分析结果 JSON。

【项目编号】{contract_no}
【前项合同】{前项合同 JSON}
【后项合同】{后项合同 JSON}

请按以下 JSON 格式输出：

{
  "rate": "毛利率，(前项金额-后项金额)/前项金额",
  "rate_level": "正常/低毛利/利润倒挂",
  "similarity": "完全一致/有一致性风险/完全不一致",
  "analysis": "详细分析文本：1.毛利率情况 2.关键条款差异 3.风险点总结"
}
```

### 验收报告对比分析 Prompt

```
你是一个验收报告对比分析专家。请对比同一项目的前项和后项验收报告，返回分析结果 JSON。

【项目编号】{contract_no}
【前项验收报告】{前项验收 JSON}
【后项验收报告】{后项验收 JSON}

请按以下 JSON 格式输出：

{
  "similarity": "完全一致/有一致性风险/完全不一致",
  "analysis": "详细分析文本：1.验收内容差异 2.验收日期逻辑 3.验收结论一致性 4.风险点"
}
```

---

## 配置

Agent 使用 `agent/config.yaml` 配置文件：

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
```

**运行环境要求**：
- Python 3.12 (TeleAgent 内置运行时: `C:\Users\vanze\.local\share\TeleAgent\runtimes\python\python.exe`)
- 依赖: httpx, pyyaml, PyMuPDF, pdfplumber, pdf2image, paddleocr, python-docx, openpyxl
- 后端服务运行在 `http://localhost:8000`
- PostgreSQL 本地服务 (contract_review 数据库)
- MinIO / Redis Docker 容器运行中

---

## 后端 API 参考

### 文档提交流程

| 方法 | 路径 | 认证 | 用途 |
|:---|:---|:---|:---|
| GET | `/api/v1/contracts/check` | - | 合同查重 (contract_no + contract_type) |
| GET | `/api/v1/acceptance/check` | - | 验收查重 (contract_no + acceptance_type) |
| POST | `/api/v1/files/upload` | X-API-Key | 文件上传 MinIO |
| POST | `/api/v1/contracts` | X-API-Key | 推送合同（自动更新 has_*） |
| POST | `/api/v1/acceptance` | X-API-Key | 推送验收报告（自动更新 has_*） |
| GET | `/api/v1/contracts/cards` | - | 项目卡片列表（前后项并排） |
| GET | `/api/v1/contracts` | - | 合同列表（分页） |
| GET | `/api/v1/contracts/{id}` | - | 合同详情 |
| PUT | `/api/v1/contracts/{id}` | JWT | 修正合同 |
| POST | `/api/v1/contracts/{id}/verify` | JWT | 人工确认 |
| DELETE | `/api/v1/contracts/{id}` | JWT | 删除合同（回置 has_*） |
| GET | `/api/v1/acceptance` | - | 验收列表（分页） |
| GET | `/api/v1/acceptance/{id}` | - | 验收详情 |
| PUT | `/api/v1/acceptance/{id}` | JWT | 修正验收报告 |
| POST | `/api/v1/acceptance/{id}/verify` | JWT | 人工确认 |
| DELETE | `/api/v1/acceptance/{id}` | JWT | 删除验收报告（回置 has_*） |

### 风险分析流程

| 方法 | 路径 | 认证 | 用途 |
|:---|:---|:---|:---|
| GET | `/api/v1/projects` | - | 项目列表（含 has_* + llm_analyzed） |
| GET | `/api/v1/projects/{contract_no}` | - | 项目详情 |
| PUT | `/api/v1/projects/{contract_no}` | JWT | 更新项目（project_risk, llm_analyzed, audit_status） |
| POST | `/api/v1/contract-analysis` | X-API-Key | 合同分析 UPSERT |
| GET | `/api/v1/contract-analysis/{contract_no}` | - | 查询合同分析 |
| GET | `/api/v1/contract-analysis` | - | 合同分析列表 |
| POST | `/api/v1/contract-analysis/{contract_no}/verify` | JWT | 人工确认合同分析 |
| POST | `/api/v1/acceptance-analysis` | X-API-Key | 验收分析 UPSERT |
| GET | `/api/v1/acceptance-analysis/{contract_no}` | - | 查询验收分析 |
| GET | `/api/v1/acceptance-analysis` | - | 验收分析列表 |
| POST | `/api/v1/acceptance-analysis/{contract_no}/verify` | JWT | 人工确认验收分析 |

### 仪表盘与报表

| 方法 | 路径 | 认证 | 用途 |
|:---|:---|:---|:---|
| GET | `/api/v1/dashboard/overview` | - | 总览统计 |
| GET | `/api/v1/dashboard/city-stats` | - | 按地市统计 |
| GET | `/api/v1/reports/contract-consistency` | JWT | 合同一致性报表 |
| GET | `/api/v1/reports/acceptance-consistency` | JWT | 验收一致性报表 |
| GET | `/api/v1/reports/low-margin` | JWT | 低毛利项目报表 |
| GET | `/api/v1/reports/high-risk` | JWT | 高风险项目报表 |
| GET | `/api/v1/reports/export` | JWT | 导出 Excel |

### ContractCreate 字段

```json
{
  "contract_no": "XYJAEXJCI250500015",
  "contract_type": "前项",
  "type_judge_basis": "文件名:xxx.pdf",
  "party_a": "甲方名称",
  "party_b": "乙方名称",
  "our_role": "乙方",
  "signing_date": "2025-01-15",
  "contract_period": "工期描述",
  "total_amount": 1000000.00,
  "amount_uppercase": "壹佰万元整",
  "tax_rate": 0.06,
  "payment_terms": "付款条款...",
  "delivery_terms": "交付条款...",
  "acceptance_terms": "验收条款...",
  "breach_terms": "违约责任...",
  "warranty_terms": "质保条款...",
  "ip_terms": "知识产权条款...",
  "other_key_terms": "其他关键条款...",
  "source_file_name": "黑龙江省（鹤岗）-XYJAEXJCI250500015-张三.pdf"
}
```

### ContractAnalysisCreate 字段（UPSERT）

```json
{
  "contract_no": "XYJAEXJCI250500016",
  "rate": 0.10,
  "rate_level": "正常",
  "similarity": "完全一致",
  "analysis": "毛利率10%，条款无显著差异..."
}
```

### AcceptanceAnalysisCreate 字段（UPSERT）

```json
{
  "contract_no": "XYJAEXJCI250500016",
  "similarity": "完全一致",
  "analysis": "验收内容一致，日期逻辑合理..."
}
```

---

## 对话交互示例

### 提交合同

```
用户：[发送文件] 前项合同_鹤岗.pdf

Agent：收到文件，正在分析文档内容...
       判断文档类型：合同
       从文档识别到项目名称：黑龙江省（鹤岗）传输管线工程施工服务项目
       合同编号：XYJAEXJCI250500015
       建议命名：黑龙江省（鹤岗）传输管线工程施工服务项目-XYJAEXJCI250500015-admin.pdf
       请指定上传人员（不指定则默认 admin）：

用户：张三

Agent：规范名称为：...-XYJAEXJCI250500015-张三.pdf
       正在查重... 不存在，可以提交。
       正在上传文件到 MinIO... 完成。
       正在 LLM 提取结构化数据... 完成。
       正在推送到服务器... 完成（has_front_contract 已置 true）

       合同已提交：
       - 项目：黑龙江省（鹤岗）传输管线工程施工服务项目
       - 合同编号：XYJAEXJCI250500015
       - 类型：前项
       - 金额：2,740,000.00 元
```

### 风险分析

```
用户：跑一下风险分析

Agent：正在检查所有项目的分析条件...
       ┌────────────────────────────────┬─────────┬──────────┐
       │ contract_no                    │ 条件满足 │ 状态     │
       ├────────────────────────────────┼─────────┼──────────┤
       │ XYJAEXJCI250500015 (鹤岗)      │ ✗       │ 缺少验收 │
       │ XYJAEXJCI250500016 (伊春)      │ ✓       │ 可分析   │
       │ XYJAEXJCI250500017 (齐齐哈尔)  │ ✗       │ 缺少验收 │
       │ XYJAEXJCI250500018 (哈尔滨)    │ ✓       │ 可分析   │
       └────────────────────────────────┴─────────┴──────────┘

       共 2 个项目满足条件，开始逐个分析...

       [1/2] XYJAEXJCI250500016 分析完成：
       - 毛利率：10.00%（正常）
       - 合同条款一致性：完全一致
       - 验收报告一致性：完全一致
       - 综合风险：低风险

       [2/2] XYJAEXJCI250500018 分析完成：
       - 毛利率：3.00%（低毛利）
       - 合同条款一致性：有一致性风险
       - 验收报告一致性：完全一致
       - 综合风险：高风险

       ⚠️ 高风险项目：1 个（XYJAEXJCI250500018）
       请前往前端查看详细分析结果并确认。
```

### 重新分析

```
用户：重新分析一下 XYJAEXJCI250500016

Agent：好的，重置分析状态并重新分析...
       PUT /api/v1/projects/XYJAEXJCI250500016 {"llm_analyzed": false}
       重新执行 LLM 分析...
       重新分析完成，结果如下：...
```

---

## 错误处理

| 场景 | 处理方式 |
|:---|:---|
| 文档提取失败 | 提示用户文件不清晰或格式不支持，终止流程 |
| 网络/服务器错误 | 提示用户检查后端服务是否运行 |
| 用户拒绝建议的文件名 | 询问用户手动输入文件名 |
| 重复提交 | 查重拦截，提示已存在 |
| LLM 提取金额格式不标准 | 正则清理（去逗号、去单位），输出纯数字 |
| 前项金额为 0 导致除零 | rate 标记为 null，rate_level 标记为"无效"，不计入风险判定 |
| 用户同时提交多个文件 | 逐个串行处理 |
| 文件不是合同也不是验收报告 | 提示用户不支持该类型 |

---

## 注意事项

1. **查重必做**：推送前必须先调用 check API 确认不重复
2. **文件命名规范**：`项目名称-合同编号-上传人员.扩展名`
3. **LLM 分析需用户指令**：不自动触发风险分析
4. **LLM 配置必须**：需在 config.yaml 中配置有效凭证
5. **大文件处理**：超大 PDF（100+ 页）可能 OCR 超时，建议分批处理
6. **项目材料目录**：`A:\Inbox\contract\恒天项目材料\` 包含 4 个子项目

## Resources

### scripts/

- **auto_extract.py** — 主入口脚本，批量扫描目录并处理合同/验收文件
- **push_contract.py** — 读取已提取的 JSON 文件，推送到后端
- **push_acceptance.py** — 读取已提取的 JSON 文件，推送到后端

### references/

- **api_reference.md** — 后端 API 完整参考文档
- **directory_guide.md** — 恒天项目材料目录结构与预提取数据说明
