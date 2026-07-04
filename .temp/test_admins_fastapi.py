"""使用 TestClient 测试 admins 接口以获取详细错误信息。"""
import sys
sys.path.insert(0, r"A:\Inbox\contract-review-system\backend")

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Login first
resp = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
print("Login:", resp.status_code)
data = resp.json()
print(data.get("data", {}).get("admin", {}))

token = data["data"]["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Test admins list
resp2 = client.get("/api/v1/admins", headers=headers)
print(f"\nAdmins list: {resp2.status_code}")
if resp2.status_code != 200:
    print("Response body:", resp2.text[:500])
else:
    print(resp2.json())
