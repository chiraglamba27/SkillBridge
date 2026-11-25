"""Unit tests for FastAPI endpoints in src/api.py."""

from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_roles():
    response = client.get("/api/roles")
    assert response.status_code == 200
    data = response.json()
    assert "roles" in data
    assert len(data["roles"]) == 8
    assert "Machine Learning Engineer" in data["roles"]
    assert "default_weights" in data
    assert "sample_resumes" in data


def test_analyze_endpoint():
    payload = {
        "resume_text": "Experienced Python and Scikit-Learn developer. Built Pandas data models and SQL databases.",
        "target_role": "Machine Learning Engineer",
    }
    response = client.post("/api/analyze", data=payload)
    assert response.status_code == 200
    data = response.json()
    assert "gap_results" in data
    assert "recommendations" in data
    assert "readability" in data
    assert "leaderboard" in data
    assert "graph_data" in data
    assert "nodes" in data["graph_data"]
    assert "edges" in data["graph_data"]
    assert len(data["graph_data"]["nodes"]) > 0
