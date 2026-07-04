# -*- coding: utf-8 -*-
"""Push LLM analysis results to the contract review system.
Performs: contract analysis, acceptance analysis, and project risk update for both projects.
"""
import json
import urllib.request

BASE = "http://localhost:8000/api/v1"
API_KEY = "change-me-to-a-random-agent-api-key"
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

def post(url, data, headers=None):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

def put(url, data, headers=None):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="PUT")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

# Step 1: Login to get JWT token
print("=" * 60)
print("Step 1: Login to get JWT token")
login_resp = post(f"{BASE}/auth/login", {
    "username": ADMIN_USER,
    "password": ADMIN_PASS
})
jwt_token = login_resp.get("data", {}).get("access_token", "")
if not jwt_token:
    # Try alternate response structure
    jwt_token = login_resp.get("access_token", "")
print(f"  JWT token obtained: {jwt_token[:20]}...")

agent_headers = {"X-API-Key": API_KEY}
admin_headers = {"Authorization": f"Bearer {jwt_token}"}

# ============================================================
# Step 2: Push Contract Analysis for 伊春 (XYJAEXJCI250500016)
# ============================================================
print("\n" + "=" * 60)
print("Step 2: Push contract analysis - 伊春 (XYJAEXJCI250500016)")

yichun_contract_analysis = {
    "contract_no": "XYJAEXJCI250500016",
    "rate": 0.10,
    "rate_level": "正常",
    "similarity": "有一致性风险",
    "analysis": """【毛利率分析】前项合同金额166.00万元，后项合同金额149.40万元，毛利率10.00%，属正常水平。

【主体一致性】前项乙方（中电信数智黑龙江分公司）与后项甲方一致，合同链条完整。

【条款比对】
1. 工期：前项30天 vs 后项30天，一致。
2. 税率：均为9%，一致。
3. 付款方式：前项与后项均为预付款30%+进度款50%+尾款20%，后项额外约定质量保证金（不超3%）和安全生产费（2%），属合理补充。
4. 验收条款：前项为单次验收（5个工作日内），后项为初验+终验两阶段（初验15个工作日），后项验收流程更严格，存在差异。
5. 违约金条款：前项工期违约按周递增（1%/2%/3%），后项工期违约按天计算（1%/天），后项违约成本显著更高，对我方（甲方角色）有利但需关注履约风险。
6. 保修期：均为验收合格后12个月，一致。
7. 分包条款：均禁止分包、转包，一致。

【风险提示】后项合同工期违约金（1%/天）远严于前项（1%/周起步），若工期延误，我方面临的违约成本远高于前项保障，存在资金风险敞口。"""
}

resp = post(f"{BASE}/contract-analysis", yichun_contract_analysis, agent_headers)
print(f"  Response: {json.dumps(resp, ensure_ascii=False)}")

# ============================================================
# Step 3: Push Contract Analysis for 哈尔滨 (XYJAEXJCI250500018)
# ============================================================
print("\n" + "=" * 60)
print("Step 3: Push contract analysis - 哈尔滨 (XYJAEXJCI250500018)")

haerbin_contract_analysis = {
    "contract_no": "XYJAEXJCI250500018",
    "rate": 0.03,
    "rate_level": "低毛利",
    "similarity": "有一致性风险",
    "analysis": """【毛利率分析】前项合同金额445.00万元，后项合同金额431.65万元，毛利率仅3.00%，低于5%预警线，属低毛利项目，利润空间极薄。

【主体一致性】前项乙方（中电信数智黑龙江分公司）与后项甲方一致，合同链条完整。

【条款比对】
1. 工期：前项30天 vs 后项30天，一致。
2. 税率：均为9%，一致。
3. 付款方式：前项仅约定"按进度付款"，后项约定"按进度付款（分期付款）"并增加安全生产费（2%），前项付款条件过于简略。
4. 验收条款：前项为单次验收（5个工作日内），后项为初验+终验两阶段，且后项试运行期、终验时限均未填写，存在条款缺失。
5. 违约金条款：前项工期违约按周递增（1%/2%/3%），后项工期违约按天计算（1%/天），后项违约成本显著更高。
6. 保修期：均为12个月，一致。
7. 分包条款（重要差异）：前项允许经发包人书面同意的非主体分包（4.6.1-4.6.5条），后项明确禁止任何分包和转包（4.2.3条），存在条款矛盾。
8. 签约日期：前后项合同均缺失签约日期。

【风险提示】
1. 毛利率仅3.00%，接近盈亏平衡线，任何成本超支都可能导致亏损。
2. 分包条款前后矛盾——前项允许分包但后项禁止，若实际施工中需要分包将面临条款冲突。
3. 后项合同多项关键条款缺失（试运行期、终验时限、迟延服务违约金比例等），存在履约争议风险。
4. 两份合同均无签约日期，合同生效时间无法确认。"""
}

resp = post(f"{BASE}/contract-analysis", haerbin_contract_analysis, agent_headers)
print(f"  Response: {json.dumps(resp, ensure_ascii=False)}")

# ============================================================
# Step 4: Push Acceptance Analysis for 伊春 (XYJAEXJCI250500016)
# ============================================================
print("\n" + "=" * 60)
print("Step 4: Push acceptance analysis - 伊春 (XYJAEXJCI250500016)")

yichun_acceptance_analysis = {
    "contract_no": "XYJAEXJCI250500016",
    "similarity": "有一致性风险",
    "analysis": """【验收结论比对】前项验收结论为"经甲乙双方同意，本项目通过验收"（2025-07-30），后项验收结论为"合格"（2025-07-02），验收结论均为通过。

【时间逻辑分析】
1. 前项验收日期2025-07-30，后项验收日期2025-07-02，后项验收早于前项约28天。
2. 后项合同签订日期为2025-07-10，但后项验收日期为2025-07-02，验收日期早于合同签订日期，存在时间逻辑矛盾。
3. 后项施工日志记录施工日期为2025年7月15日至7月30日，但验收日期（7月2日）早于施工开始日期，进一步确认时间矛盾。
4. 完工验收报告显示甲方签署日期为2025年7月2日，乙方签署日期为2025年7月28日，签署时间跨度较大。

【内容比对】前项验收报告内容较完整，包含项目名称、甲乙方、验收日期、验收结论、项目进度、项目地点和项目内容。后项验收报告为内页资料汇总，包含工程开工报告、施工组织设计、施工日志、隐蔽工程、完工验收报告、工程总结等，资料较丰富。

【风险提示】后项验收日期早于合同签订日期和施工开始日期，存在时间逻辑矛盾，建议核实实际验收时间。"""
}

resp = post(f"{BASE}/acceptance-analysis", yichun_acceptance_analysis, agent_headers)
print(f"  Response: {json.dumps(resp, ensure_ascii=False)}")

# ============================================================
# Step 5: Push Acceptance Analysis for 哈尔滨 (XYJAEXJCI250500018)
# ============================================================
print("\n" + "=" * 60)
print("Step 5: Push acceptance analysis - 哈尔滨 (XYJAEXJCI250500018)")

haerbin_acceptance_analysis = {
    "contract_no": "XYJAEXJCI250500018",
    "similarity": "完全一致",
    "analysis": """【验收结论比对】前项验收结论为"合格"（2025-07-23），后项验收结论为"合格"（2025-07-30），验收结论一致。

【时间逻辑分析】前项验收日期（7月23日）早于后项验收日期（7月30日），符合先完成上家验收再完成下家验收的业务逻辑，时间顺序合理。

【内容比对】两份验收报告内容均极其简略，仅包含"工程施工验收是保证工程质量、安全、可靠的关键环节。经双方同意，通过验收。"，缺少项目名称、甲乙方信息、项目进度、项目内容等关键要素。

【风险提示】验收报告内容过于简略，缺少关键验收要素，建议补充完善验收报告内容。"""
}

resp = post(f"{BASE}/acceptance-analysis", haerbin_acceptance_analysis, agent_headers)
print(f"  Response: {json.dumps(resp, ensure_ascii=False)}")

# ============================================================
# Step 6: Update Project Risk - 伊春 → 低风险
# ============================================================
print("\n" + "=" * 60)
print("Step 6: Update project risk - 伊春 → 低风险")

resp = put(f"{BASE}/projects/XYJAEXJCI250500016", {
    "project_risk": "低风险",
    "llm_analyzed": True
}, admin_headers)
print(f"  Response: {json.dumps(resp, ensure_ascii=False)}")

# ============================================================
# Step 7: Update Project Risk - 哈尔滨 → 高风险
# ============================================================
print("\n" + "=" * 60)
print("Step 7: Update project risk - 哈尔滨 → 高风险")

resp = put(f"{BASE}/projects/XYJAEXJCI250500018", {
    "project_risk": "高风险",
    "llm_analyzed": True
}, admin_headers)
print(f"  Response: {json.dumps(resp, ensure_ascii=False)}")

print("\n" + "=" * 60)
print("ALL DONE!")
