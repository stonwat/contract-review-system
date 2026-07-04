import urllib.request
import json

req = urllib.request.Request(
    'http://localhost:8000/api/v1/auth/login',
    data=json.dumps({"username": "admin", "password": "admin123"}).encode(),
    headers={"Content-Type": "application/json"},
)
resp = urllib.request.urlopen(req)
data = json.loads(resp.read().decode())
print(json.dumps(data, indent=2, ensure_ascii=False))
print()
print("=== role ===", data["data"]["admin"]["role"])
print("=== city ===", data["data"]["admin"]["city"])
