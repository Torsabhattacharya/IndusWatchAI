import requests
import json
from datetime import datetime

# Test data
test_data = {
    "machine_id": "TEST001",
    "machine_type": "CNC",
    "temperature": 75.5,
    "vibration": 0.35,
    "pressure": 101.2,
    "rpm": 1450,
    "is_anomaly": False,
    "failure_risk": 0.0,
    "health_score": 100.0
}

# Send test request
response = requests.post(
    "http://localhost:8000/sensor-data",
    json=test_data,
    headers={"Content-Type": "application/json"}
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test health endpoint
health = requests.get("http://localhost:8000/health")
print(f"\nHealth: {health.json()}")