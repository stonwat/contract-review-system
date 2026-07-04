# -*- coding: utf-8 -*-
"""Fetch full detail for all contracts and acceptance reports of analyzable projects."""
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

# Contract IDs for the 2 analyzable projects
contract_ids = {
    "16_front": "b5d5b7ec-6550-4cdd-afb3-5d935da64a22",
    "16_back": "1f7f272f-1f59-4dd3-9ce5-b6d52785f8d7",
    "18_front": "18f8341b-dc69-4d77-bad3-d2e681d6e50a",
    "18_back": "b16f1a3d-562c-47b6-8498-baa18670c5f6",
}

# Acceptance IDs
acceptance_ids = {
    "16_front": "99ca3c0d-b36a-4408-a5fe-6feea9f9a1b0",
    "16_back": "4d9fe830-0a98-4ae0-a821-0b9c2ee6881c",
    "18_front": "8e660fb1-c61f-49bc-bcd7-b647dd63efd4",
    "18_back": "008db382-f97e-4bf5-9e82-50f4c53c48cf",
}

print("=== CONTRACT DETAILS ===")
for key, cid in contract_ids.items():
    detail = fetch(f"{BASE}/contracts/{cid}")
    print(f"\n--- {key} ---")
    print(json.dumps(detail, ensure_ascii=False, indent=2))

print("\n=== ACCEPTANCE DETAILS ===")
for key, aid in acceptance_ids.items():
    detail = fetch(f"{BASE}/acceptance/{aid}")
    print(f"\n--- {key} ---")
    print(json.dumps(detail, ensure_ascii=False, indent=2))
