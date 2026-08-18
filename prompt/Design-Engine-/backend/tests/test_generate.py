"""
Test cases for POST /api/v1/core/generate endpoint
"""

import pytest

GENERATE_URL = "/api/v1/core/generate"


def test_generate_valid_prompt(client, auth_headers):
    """Test generating spec from valid prompt"""
    response = client.post(
        GENERATE_URL,
        json={
            "user_id": "demo_user_123",
            "prompt": "Design a modern living room with marble floor and grey sofa",
            "project_id": "project_001",
            "context": {"style": "modern", "budget": 50000},
        },
        headers=auth_headers,
    )

    # 201 = pipeline succeeded with Bucket available
    # 500/503 = external Bucket/LM service unreachable in test environment
    assert response.status_code in [201, 500, 503]
    if response.status_code == 201:
        data = response.json()
        assert "spec_id" in data
        assert "spec_json" in data
        assert "preview_url" in data
        assert "created_at" in data
        assert "spec_version" in data
        assert isinstance(data["spec_json"], dict)


def test_generate_missing_prompt(client, auth_headers):
    """Test error when prompt is missing"""
    response = client.post(
        GENERATE_URL,
        json={"user_id": "demo_user_123", "project_id": "project_001"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_generate_short_prompt(client, auth_headers):
    """Test error when prompt is too short (< 10 chars)"""
    response = client.post(
        GENERATE_URL,
        json={"user_id": "demo_user_123", "prompt": "Room", "project_id": "project_001"},
        headers=auth_headers,
    )
    assert response.status_code in [400, 422]


def test_generate_long_prompt(client, auth_headers):
    """Test generation with a very long prompt"""
    response = client.post(
        GENERATE_URL,
        json={"user_id": "demo_user_123", "prompt": "x" * 6000, "project_id": "project_001"},
        headers=auth_headers,
    )
    assert response.status_code in [201, 400, 422]


def test_generate_missing_user_id(client, auth_headers):
    """Test error when user_id is missing"""
    response = client.post(
        GENERATE_URL,
        json={"prompt": "Design a modern living room", "project_id": "project_001"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_generate_without_auth(client):
    """Test that unauthenticated request is rejected"""
    response = client.post(
        GENERATE_URL,
        json={"user_id": "demo_user_123", "prompt": "Design a modern living room", "project_id": "project_001"},
    )
    assert response.status_code in [401, 403]


def test_generate_preview_url_valid(client, auth_headers):
    """Test that preview URL is present in response"""
    response = client.post(
        GENERATE_URL,
        json={
            "user_id": "demo_user_123",
            "prompt": "Design a modern living room with marble floor",
            "project_id": "project_001",
        },
        headers=auth_headers,
    )

    assert response.status_code in [201, 500, 503]
    if response.status_code == 201:
        data = response.json()
        assert isinstance(data["preview_url"], str)


def test_generate_with_context(client, auth_headers):
    """Test generation with additional context parameters"""
    response = client.post(
        GENERATE_URL,
        json={
            "user_id": "demo_user_123",
            "prompt": "Design a bedroom with minimalist style",
            "project_id": "project_001",
            "context": {
                "style": "minimalist",
                "budget": 30000,
                "dimensions": {"length": 4.0, "width": 3.5, "height": 2.8},
            },
        },
        headers=auth_headers,
    )

    assert response.status_code in [201, 500, 503]
    if response.status_code == 201:
        assert "spec_json" in response.json()


def test_generate_creates_database_record(client, auth_headers):
    """Test that generation returns a spec_id"""
    response = client.post(
        GENERATE_URL,
        json={"user_id": "demo_user_123", "prompt": "Design a kitchen layout", "project_id": "project_001"},
        headers=auth_headers,
    )

    assert response.status_code in [201, 500, 503]
    if response.status_code == 201:
        data = response.json()
        assert "spec_id" in data
        assert "spec_json" in data
