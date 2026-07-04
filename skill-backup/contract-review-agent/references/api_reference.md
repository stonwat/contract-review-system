---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: '286a3c23-aa56-45b3-be7a-f01739f1c0a8'
  PropagateID: '286a3c23-aa56-45b3-be7a-f01739f1c0a8'
  ReservedCode1: '2abf04f0-6d06-4b09-adb1-0b1f7b69f851'
  ReservedCode2: '2abf04f0-6d06-4b09-adb1-0b1f7b69f851'
---

# 后端 API 参考文档

> 基于 `A:\Inbox\contract-review-system\backend\app\api\v1\` 下的路由模块整理
> 对齐 V3.2 数据库设计 + V2.0 工作流程

## 基础信息

- Base URL: `http://localhost:8000/api/v1`
- 认证方式:
  - **Agent 认证**: Header `X-API-Key: <AGENT_API_KEY>` (用于 Agent 推送数据)
  - **管理员认证**: Header `Authorization: Bearer <JWT_TOKEN>` (用于人工操作)

---

## 合同 API (`/contracts`)

### GET /contracts/check — 合同查重

**Auth**: X-API-Key

**Query Params**:
- `contract_no` (必填): 合同编号
- `contract_type` (必填): "前项" | "后项"

**Response**:
```json
{
  "code": 0,
  "data": {
    "exists": false,
    "contract_id": null
  }
}
```

### POST /contracts — Agent 推送合同

**Auth**: X-API-Key

**Request Body** (ContractCreate):
```json
{
  "contract_no": "XYJAEXJCI250500015",
  "contract_type": "前项",
  "type_judge_basis": "文件名:前项合同.pdf",
  "party_a": "中国电信黑龙江分公司",
  "party_b": "大庆恒天技术有限公司",
  "our_role": "乙方",
  "signing_date": "2025-03-10",
  "contract_period": "2025年3月至2025年12月",
  "total_amount": 3580000.00,
  "amount_uppercase": "叁佰伍拾捌万元整",
  "tax_rate": 0.06,
  "payment_terms": "按工程进度分三期付款...",
  "delivery_terms": "乙方应于合同签订后...",
  "acceptance_terms": "工程完工后甲方组织验收...",
  "breach_terms": "任何一方违约...",
  "warranty_terms": "质保期为验收合格后12个月",
  "ip_terms": null,
  "other_key_terms": null,
  "source_file_name": "黑龙江省（鹤岗）传输管线工程施工服务项目-XYJAEXJCI250500015-张三.pdf"
}
```

**Response**:
```json
{
  "code": 0,
  "data": {
    "contract_id": "uuid",
    "contract_no": "XYJAEXJCI250500015",
    "project_created": true
  }
}
```

**注意**:
- 自动创建 Project（若 contract_no 对应的项目不存在）
- 自动更新 projects 表布尔标记：contract_type="前项" → has_front_contract=true；contract_type="后项" → has_back_contract=true
- 不再包含 line_items、source_file_hash、ocr_engine、llm_model、ocr_raw_text 字段

### GET /contracts — 合同列表

**Query Params**: `page`, `page_size`, `contract_no`(模糊), `contract_type`, `verified`

**Response**:
```json
{
  "code": 0,
  "data": {
    "items": [{"id": "uuid", "contract_no": "...", "contract_type": "前项", "city": "鹤岗", ...}],
    "total": 10,
    "page": 1,
    "page_size": 20
  }
}
```

### GET /contracts/cards — 项目卡片列表

**Query Params**: `city`, `verified`, `keyword`

返回按 contract_no 分组的卡片数据，每个卡片包含前后项合同并排展示 + has_* 标记 + llm_analyzed + project_risk。

**Response**:
```json
{
  "code": 0,
  "data": [
    {
      "contract_no": "XYJAEXJCI250500015",
      "project_name": "黑龙江省（鹤岗）传输管线工程施工服务项目",
      "city": "鹤岗",
      "has_front_contract": true,
      "has_back_contract": true,
      "has_front_acceptance": false,
      "has_back_acceptance": false,
      "llm_analyzed": false,
      "project_risk": null,
      "audit_status": null,
      "front_contract": {"id": "uuid", "contract_no": "...", "total_amount": 2740000.00, ...},
      "back_contract": {"id": "uuid", "contract_no": "...", "total_amount": 2500000.00, ...}
    }
  ]
}
```

### GET /contracts/{id} — 合同详情

### PUT /contracts/{id} — 修正合同 (JWT)

### POST /contracts/{id}/verify — 人工确认 (JWT)

**Body**: `{"verified_by": "admin"}`

### DELETE /contracts/{id} — 删除合同 (JWT)

删除后自动回置 projects 表对应的 has_* 标记。

---

## 验收报告 API (`/acceptance`)

### GET /acceptance/check — 验收报告查重

**Auth**: X-API-Key

**Query Params**:
- `contract_no` (必填): 合同编号
- `acceptance_type` (必填): "前项" | "后项"

**Response**:
```json
{
  "code": 0,
  "data": {
    "exists": false
  }
}
```

### POST /acceptance — Agent 推送验收报告

**Auth**: X-API-Key

**Request Body** (AcceptanceCreate):
```json
{
  "acceptance_no": "YS-XMJAEXJCI250500015-001",
  "contract_no": "XYJAEXJCI250500015",
  "acceptance_type": "前项",
  "type_judge_basis": "文件名:前项验收报告.pdf",
  "acceptance_content": "验收内容摘要...",
  "acceptance_date": "2025-06-30",
  "acceptance_result": "合格",
  "source_file_name": "黑龙江省（鹤岗）-XYJAEXJCI250500015-验收报告-张三.pdf"
}
```

**注意**:
- 自动更新 projects 表布尔标记：acceptance_type="前项" → has_front_acceptance=true；acceptance_type="后项" → has_back_acceptance=true
- 不再包含 source_file_hash、ocr_engine、llm_model、ocr_raw_text 字段

### GET /acceptance — 验收列表

**Query Params**: `page`, `page_size`, `contract_no`(模糊), `verified`

### GET /acceptance/{id} — 验收详情

### PUT /acceptance/{id} — 修正验收报告 (JWT)

### POST /acceptance/{id}/verify — 人工确认 (JWT)

### DELETE /acceptance/{id} — 删除验收报告 (JWT)

删除后自动回置 projects 表对应的 has_* 标记。

---

## 项目 API (`/projects`)

### GET /projects — 项目列表

**Query Params**: `city`, `llm_analyzed`, `project_risk`, `audit_status`, `page`, `page_size`

**Response**:
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "contract_no": "XYJAEXJCI250500015",
        "project_name": "黑龙江省（鹤岗）...",
        "city": "鹤岗",
        "has_front_contract": true,
        "has_back_contract": true,
        "has_front_acceptance": false,
        "has_back_acceptance": false,
        "llm_analyzed": false,
        "project_risk": null,
        "audit_status": null,
        "audited_by": null,
        "audited_at": null
      }
    ],
    "total": 4
  }
}
```

### GET /projects/{contract_no} — 项目详情

### PUT /projects/{contract_no} — 更新项目 (JWT)

**Request Body** (ProjectUpdate，所有字段可选):
```json
{
  "project_risk": "低风险",
  "llm_analyzed": true,
  "audit_status": "已通过"
}
```

**注意**: `audited_by` 和 `audited_at` 由后端自动填充（从 JWT 中提取用户名 + 当前时间）。

---

## 合同分析 API (`/contract-analysis`)

### POST /contract-analysis — 合同分析 UPSERT

**Auth**: X-API-Key

**Request Body** (ContractAnalysisCreate):
```json
{
  "contract_no": "XYJAEXJCI250500016",
  "rate": 0.10,
  "rate_level": "正常",
  "similarity": "完全一致",
  "analysis": "毛利率10%，条款无显著差异..."
}
```

**注意**: UPSERT 语义 — 同 contract_no 存在则更新，不存在则创建。重新分析时 verified 字段会被重置为 false。

### GET /contract-analysis/{contract_no} — 查询合同分析

### GET /contract-analysis — 合同分析列表

**Query Params**: `page`, `page_size`, `verified`

### POST /contract-analysis/{contract_no}/verify — 人工确认 (JWT)

**Body**: `{"verified_by": "admin"}`

---

## 验收分析 API (`/acceptance-analysis`)

### POST /acceptance-analysis — 验收分析 UPSERT

**Auth**: X-API-Key

**Request Body** (AcceptanceAnalysisCreate):
```json
{
  "contract_no": "XYJAEXJCI250500016",
  "similarity": "完全一致",
  "analysis": "验收内容一致，日期逻辑合理..."
}
```

### GET /acceptance-analysis/{contract_no} — 查询验收分析

### GET /acceptance-analysis — 验收分析列表

**Query Params**: `page`, `page_size`, `verified`

### POST /acceptance-analysis/{contract_no}/verify — 人工确认 (JWT)

**Body**: `{"verified_by": "admin"}`

---

## 仪表盘 API (`/dashboard`)

### GET /dashboard/overview — 总览统计

**Response**:
```json
{
  "code": 0,
  "data": {
    "project_count": 4,
    "contract_count": 8,
    "acceptance_count": 4,
    "pending_count": 8,
    "verified_count": 0,
    "llm_analyzed_count": 2,
    "ready_count": 2,
    "front_count": 4,
    "back_count": 4,
    "high_risk_count": 1
  }
}
```

### GET /dashboard/city-stats — 按地市统计

**Response**:
```json
{
  "code": 0,
  "data": [
    {"city": "鹤岗", "project_count": 1, "contract_count": 2, "acceptance_count": 0, "high_risk_count": 0},
    {"city": "伊春", "project_count": 1, "contract_count": 2, "acceptance_count": 2, "high_risk_count": 0}
  ]
}
```

---

## 报表 API (`/reports`)

### GET /reports/contract-consistency — 合同一致性报表 (JWT)

### GET /reports/acceptance-consistency — 验收一致性报表 (JWT)

### GET /reports/low-margin — 低毛利项目报表 (JWT)

### GET /reports/high-risk — 高风险项目报表 (JWT)

### GET /reports/export — 导出 Excel (JWT)

---

## 文件 API (`/files`)

### POST /files/upload — 文件上传 MinIO

**Auth**: X-API-Key

**Body**: multipart/form-data, field: `file`

**Response**:
```json
{
  "code": 0,
  "data": {
    "object_key": "contracts/2025/07/xxx.pdf",
    "file_name": "xxx.pdf",
    "file_size": 1234567
  }
}
```

---

## 认证 API (`/auth`)

### POST /auth/login — 管理员登录

**Body**: `{"username": "admin", "password": "xxx"}`

**Response**:
```json
{
  "access_token": "jwt...",
  "token_type": "bearer"
}
```

---

## 字段变更说明 (V3.2)

相比旧版本，以下字段已移除：

| 移除字段 | 原所在表 | 原因 |
|:---|:---|:---|
| line_items | contracts (关联表) | 比对模块已移除，不再需要分项清单 |
| source_file_hash | contracts / acceptance_reports | 文件存储改由 MinIO object_key 管理 |
| ocr_engine | contracts / acceptance_reports | OCR 引擎信息不再需要持久化 |
| llm_model | contracts / acceptance_reports | LLM 模型信息不再需要持久化 |
| ocr_raw_text | contracts / acceptance_reports | 原始 OCR 文本不再持久化到数据库 |
| comparison_result | acceptance_reports | 比对模块已移除 |
| content_diff_detail | acceptance_reports | 比对模块已移除 |
| date_logic | acceptance_reports | 比对模块已移除 |
| gross_margin | projects | 毛利率改由 contract_analyses 表存储 |

> AI生成