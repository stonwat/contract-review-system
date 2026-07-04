# -*- coding: utf-8 -*-
"""Fetch all contract + acceptance data from API with proper encoding."""
import json
import urllib.request

BASE = "http://localhost:8000/api/v1"

def fetch(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
        if isinstance(raw, dict) and "data" in raw:
            data = raw["data"]
            if isinstance(data, dict) and "items" in data:
                return data["items"]
            return data
        return raw

# Get all contracts
contracts = fetch(f"{BASE}/contracts")
# Get all acceptance reports
acceptances = fetch(f"{BASE}/acceptance")

print("=== CONTRACTS ===")
for c in contracts:
    print(json.dumps(c, ensure_ascii=False, indent=2))

print("\n=== ACCEPTANCE REPORTS ===")
for a in acceptances:
    print(json.dumps(a, ensure_ascii=False, indent=2))
