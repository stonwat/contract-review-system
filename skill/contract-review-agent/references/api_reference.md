---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: '5f058104-59c4-4292-8649-7dd400e47409'
  PropagateID: '5f058104-59c4-4292-8649-7dd400e47409'
  ReservedCode1: '307c227d-88be-4d63-9976-1c7f3db23c58'
  ReservedCode2: '307c227d-88be-4d63-9976-1c7f3db23c58'
---

# 后端 API 参考文档

> 基于 `A:\Inbox\contract-review-system\backend\app\api\v1\` 下的路由模块整理

## 基础信息

- Base URL: `http://localhost:8000/api/v1`
- 认证方式:
  - **Agent 认证**: Header `X-API-Key: <AGENT_API_KEY>` (用于 Agent 推送数据)
  - **管理员认证**: Header `Authorization: Bearer <JWT_TOKEN>` (用于人工操作)

## 合同 API (`/contracts`)

### POST /contracts — Agent 推送合同

**Auth**: X-API-Key

**Request Body** (ContractCreate):
```json
{
  "contract_no": "XYJAEXJCI250500015",      // 必填
  "contract_type": "前项",                    // 必填: "前项" | "后项"
  "type_judge_basis": "文件名:前项合同.pdf",
  "party_a": "中国电信黑龙江分公司",
  "party_b": "大庆恒天技术有限公司",
  "our_role": "乙方",                         // 我方角色
  "signing_date": "2025-03-10",              // YYYY-MM-DD
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
  "source_file_name": "黑龙江省（鹤岗）传输管线工程施工服务合同.pdf",
  "source_file_hash": "sha256...",
  "ocr_raw_text": "合同全文OCR提取结果...",
  "ocr_engine": "paddleocr",
  "llm_model": "qwen2.5-72b",
  "line_items": [                             // 分项清单
    {
      "item_no": 1,
      "item_name": "传输管线敷设",
      "spec": "48芯光缆",
      "unit": "公里",
      "quantity": 25.5,
      "unit_price": 80000.00,
      "amount": 2040000.00,
      "remark": null
    }
  ]
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

**注意**: 自动创建 Project（若 contract_no 对应的项目不存在）

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

### GET /contracts/{id} — 合同详情(含分项)

### PUT /contracts/{id} — 修正合同 (JWT)

### POST /contracts/{id}/verify — 人工确认 (JWT)

**Body**: `{"verified_by": "admin"}`

### DELETE /contracts/{id} — 删除合同 (JWT)

---

## 验收报告 API (`/acceptance`)

### POST /acceptance — Agent 推送验收报告

**Auth**: X-API-Key

**Request Body** (AcceptanceCreate):
```json
{
  "acceptance_no": "YS-XMJAEXJCI250500015-001",
  "contract_id": null,                        // 可选，关联合同ID
  "contract_no": "XYJAEXJCI250500015",        // 关联合同编号
  "acceptance_type": "前项",
  "type_judge_basis": "文件名:前项验收报告.pdf",
  "acceptance_content": "验收内容摘要...",
  "acceptance_date": "2025-06-30",
  "acceptance_result": "合格",
  "source_file_name": "鹤岗上家验收报告.pdf",
  "source_file_hash": "sha256...",
  "ocr_raw_text": "验收报告全文OCR...",
  "ocr_engine": "paddleocr",
  "llm_model": "qwen2.5-72b"
}
```

### GET /acceptance — 验收列表

**Query Params**: `page`, `page_size`, `contract_no`(模糊), `verified`

### GET /acceptance/{id} — 验收详情

### PUT /acceptance/{id} — 修正验收报告 (JWT)

### POST /acceptance/{id}/verify — 人工确认 (JWT)

---

## 比对 API (`/comparisons`)

### POST /comparisons/auto — 自动配对比对

**Auth**: JWT

自动查找已确认的前项+后项合同，按 contract_no 配对，执行金额比对、分项匹配、风险生成。

### GET /comparisons — 比对列表

### GET /comparisons/{id} — 比对详情(含分项比对结果)

---

## 其他 API

### GET /dashboard/stats — 仪表盘统计
返回总览数据和 city_stats 分城市统计

### POST /files/upload — 文件上传 MinIO (X-API-Key)
**Body**: multipart/form-data, field: `file`

### GET /reports/{id}/export — 导出 Excel 报表 (JWT)

### POST /auth/login — 管理员登录
**Body**: `{"username": "admin", "password": "xxx"}`
**Response**: `{"access_token": "jwt...", "token_type": "bearer"}`

> AI生成