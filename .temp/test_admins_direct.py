import urllib.request, json

# Login
req = urllib.request.Request(
    'http://localhost:8000/api/v1/auth/login',
    data=json.dumps({"username": "admin", "password": "admin123"}).encode(),
    headers={"Content-Type": "application/json"},
)
resp = urllib.request.urlopen(req)
data = json.loads(resp.read().decode())
token = data["data"]["access_token"]
print("Login OK")

# Test admins - get error body
try:
    req2 = urllib.request.Request(
        'http://localhost:8000/api/v1/admins',
        headers={"Authorization": f"Bearer {token}"},
    )
    resp2 = urllib.request.urlopen(req2)
    data2 = json.loads(resp2.read().decode())
    print(json.dumps(data2, indent=2, ensure_ascii=False)[:300])
except urllib.error.HTTPError as e:
    print(f"Status: {e.code}")
    body = e.read().decode()
    print(f"Body: {body[:500]}")
