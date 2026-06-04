# test_all_endpoints.py
import urllib.request
import json

endpoints = [
    "usuarios",
    "coches",
    "citas",
    "servicios",
    "historial"
]

for ep in endpoints:
    url = f"http://127.0.0.1:5000/api/v1/{ep}"
    try:
        req = urllib.request.urlopen(url)
        data = json.loads(req.read().decode('utf-8'))
        print(f"Endpoint: /api/v1/{ep} -> SUCCESS, count: {len(data)}")
    except Exception as e:
        print(f"Endpoint: /api/v1/{ep} -> FAILED: {e}")
