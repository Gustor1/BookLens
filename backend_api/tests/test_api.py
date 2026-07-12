from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "recommender_model" in data["services"]

def test_public_config():
    response = client.get("/api/config/public")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data

def test_explore():
    response = client.get("/api/explore?media_type=books&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0

def test_recommendations():
    response = client.get("/api/recommendations?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert "discover" in data
    assert "ecofiction" in data

def test_feedback():
    response = client.post("/api/profile/feedback", json={
        "media_id": "book-1",
        "media_type": "books",
        "feedback_type": "like"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"
