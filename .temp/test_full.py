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
print("Login OK, token:", token[:20] + "...")

# Test admins
try:
    req2 = urllib.request.Request(
        'http://localhost:8000/api/v1/admins',
        headers={"Authorization": f"Bearer {token}"},
    )
    resp2 = urllib.request.urlopen(req2)
    data2 = json.loads(resp2.read().decode())
    print(json.dumps(data2, indent=2, ensure_ascii=False))
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}:")
    print(e.read().decode())

# Test cities
try:
    req3 = urllib.request.Request(
        'http://localhost:8000/api/v1/cities',
        headers={"Authorization": f"Bearer {token}"},
    )
    resp3 = urllib.request.urlopen(req3)
    data3 = json.loads(resp3.read().decode())
    print("\n=== cities ===")
    print(json.dumps(data3, indent=2, ensure_ascii=False))
except urllib.error.HTTPError as e:
    print(f"\nCities Error {e.code}:")
    print(e.read().decode())
