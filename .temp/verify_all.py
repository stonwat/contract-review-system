# -*- coding: utf-8 -*-
"""Verify all analysis records are stored correctly."""
import json
import urllib.request

BASE = "http://localhost:8000/api/v1"

def fetch(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
        if isinstance(raw, dict) and "data" in raw:
            return raw["data"]
        return raw

# Check contract analysis records
print("=== Contract Analysis Records ===")
ca = fetch(f"{BASE}/contract-analysis")
items = ca if isinstance(ca, list) else ca.get("items", ca) if isinstance(ca, dict) else []
if isinstance(items, list):
    for item in items:
        print(f"\n  contract_no: {item.get('contract_no')}")
        print(f"  rate: {item.get('rate')}")
        print(f"  rate_level: {item.get('rate_level')}")
        print(f"  similarity: {item.get('similarity')}")
        print(f"  verified: {item.get('verified')}")
        analysis = item.get('analysis', '')
        print(f"  analysis (first 100 chars): {analysis[:100]}...")
else:
    print(f"  Raw: {json.dumps(ca, ensure_ascii=False)[:500]}")

# Check acceptance analysis records
print("\n=== Acceptance Analysis Records ===")
aa = fetch(f"{BASE}/acceptance-analysis")
items = aa if isinstance(aa, list) else aa.get("items", aa) if isinstance(aa, dict) else []
if isinstance(items, list):
    for item in items:
        print(f"\n  contract_no: {item.get('contract_no')}")
        print(f"  similarity: {item.get('similarity')}")
        print(f"  verified: {item.get('verified')}")
        analysis = item.get('analysis', '')
        print(f"  analysis (first 100 chars): {analysis[:100]}...")
else:
    print(f"  Raw: {json.dumps(aa, ensure_ascii=False)[:500]}")

# Check projects
print("\n=== Projects ===")
projects = fetch(f"{BASE}/projects")
items = projects if isinstance(projects, list) else projects.get("items", projects) if isinstance(projects, dict) else []
if isinstance(items, list):
    for p in items:
        print(f"  {p['contract_no']} | {p.get('city','')} | risk={p.get('project_risk','N/A')} | analyzed={p.get('llm_analyzed','N/A')}")
else:
    print(f"  Raw: {json.dumps(projects, ensure_ascii=False)[:500]}")
