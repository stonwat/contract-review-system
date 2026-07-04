# -*- coding: utf-8 -*-
"""Retry project risk updates with fresh JWT token."""
import json
import urllib.request

BASE = "http://localhost:8000/api/v1"
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

# Login fresh
print("Logging in...")
login_resp = post(f"{BASE}/auth/login", {
    "username": ADMIN_USER,
    "password": ADMIN_PASS
})
jwt_token = login_resp.get("data", {}).get("access_token", "")
if not jwt_token:
    jwt_token = login_resp.get("access_token", "")
print(f"JWT token: {jwt_token[:30]}...")

admin_headers = {"Authorization": f"Bearer {jwt_token}"}

# Update 伊春 → 低风险
print("\nUpdating 伊春 (XYJAEXJCI250500016) → 低风险...")
try:
    resp = put(f"{BASE}/projects/XYJAEXJCI250500016", {
        "project_risk": "低风险",
        "llm_analyzed": True
    }, admin_headers)
    print(f"  Success: {json.dumps(resp, ensure_ascii=False)}")
except Exception as e:
    print(f"  Error: {e}")
    if hasattr(e, 'read'):
        print(f"  Response: {e.read().decode('utf-8')}")

# Update 哈尔滨 → 高风险
print("\nUpdating 哈尔滨 (XYJAEXJCI250500018) → 高风险...")
try:
    resp = put(f"{BASE}/projects/XYJAEXJCI250500018", {
        "project_risk": "高风险",
        "llm_analyzed": True
    }, admin_headers)
    print(f"  Success: {json.dumps(resp, ensure_ascii=False)}")
except Exception as e:
    print(f"  Error: {e}")
    if hasattr(e, 'read'):
        print(f"  Response: {e.read().decode('utf-8')}")

# Verify by fetching project list
print("\nVerifying projects...")
import urllib.request
req = urllib.request.Request(f"{BASE}/projects")
with urllib.request.urlopen(req, timeout=10) as resp:
    raw = json.loads(resp.read().decode("utf-8"))
    projects = raw.get("data", {}).get("items", [])
    for p in projects:
        print(f"  {p['contract_no']} | {p.get('city','')} | risk={p.get('project_risk','N/A')} | analyzed={p.get('llm_analyzed','N/A')}")

print("\nDone!")
