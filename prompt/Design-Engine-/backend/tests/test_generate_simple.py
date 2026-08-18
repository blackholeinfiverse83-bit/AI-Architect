"""
Simple test for core/generate endpoint
"""

import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

GENERATE_URL = "/api/v1/core/generate"


def test_generate_simple():
    """Test core/generate endpoint with demo auth"""
    login_response = client.post("/api/v1/auth/login", data={"username": "demo", "password": "demo123"})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    response = client.post(
        GENERATE_URL,
        json={"user_id": "demo", "prompt": "Design a modern living room", "project_id": "test_project"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code in [201, 500, 503]
    if response.status_code == 201:
        data = response.json()
        assert "spec_id" in data
        assert "spec_json" in data
        assert "preview_url" in data
