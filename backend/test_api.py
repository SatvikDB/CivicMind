import sys
import os
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    print("✓ Health check passed")

def test_get_dashboard_stats():
    response = client.get("/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_complaints" in data
    assert data["total_complaints"] >= 18
    print(f"✓ Dashboard stats passed: {data['total_complaints']} complaints in DB")

def test_get_dashboard_analytics():
    response = client.get("/dashboard/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "category_distribution" in data
    assert "smart_insights" in data
    print(f"✓ Dashboard analytics passed: {len(data['smart_insights'])} insights generated")

def test_create_and_ai_process():
    payload = {
        "name": "Test Citizen",
        "title": "Deep Pothole near College Gate 2",
        "description": "Another complaint about the dangerous college gate pothole causing traffic skids.",
        "category": "Road",
        "location": "College Gate Road",
        "latitude": 12.3126,
        "longitude": 76.6513
    }
    response = client.post("/complaints", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "Road"
    assert data["similarity_score"] > 60.0  # Should detect duplicate with seeded pothole complaints!
    assert "DUPLICATE ALERT" in data["recommendation"]
    print(f"✓ AI Engine Post Test passed: Priority {data['priority_score']}, Similarity {data['similarity_score']}%")

if __name__ == "__main__":
    test_health()
    test_get_dashboard_stats()
    test_get_dashboard_analytics()
    test_create_and_ai_process()
    print("\nALL API & AI ENGINE INTEGRATION TESTS PASSED SUCCESSFULLY!")
