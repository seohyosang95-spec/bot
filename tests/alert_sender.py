import requests

N8N_URL = "http://localhost:5678/webhook-test/c840e964-1a62-4382-88ac-dc793dce6df2"  # n8n Webhook 노드에서 복사한 URL
STUDENT = "서효상"

data = {
    "student": STUDENT,
    "alerts": [
        {"ip": "192.168.0.10", "level": 10, "rule": 5712},  # deny로 판정될 것
        {"ip": "192.168.0.15", "level": 5, "rule": 1002}    # allow로 판정될 것
    ]
}

try:
    res = requests.post(N8N_URL, json=data)
    print(f"[n8n] POST {N8N_URL} -> {res.status_code}")
except Exception as e:
    print(f"[에러] 전송 실패: {e}")
