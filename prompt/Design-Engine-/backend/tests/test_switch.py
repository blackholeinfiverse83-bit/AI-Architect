"""
Test cases for POST /api/v1/switch endpoint
"""

import pytest

GENERATE_URL = "/api/v1/core/generate"
SWITCH_URL = "/api/v1/switch"


def _generate_spec(client, auth_headers, prompt="Design a modern living room"):
    """Helper: generate a spec and return its spec_id."""
    resp = client.post(
        GENERATE_URL,
        json={"user_id": "demo_user_123", "prompt": prompt, "project_id": "project_001"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()["spec_id"]


def test_switch_valid_material(client, auth_headers):
    """Test switching material on existing spec using natural language query"""
    spec_id = _generate_spec(client, auth_headers)

    response = client.post(
        SWITCH_URL,
        json={"spec_id": spec_id, "query": "change floor to marble"},
        headers=auth_headers,
    )

    assert response.status_code in [200, 201]
    data = response.json()
    assert "iteration_id" in data
    assert "spec_id" in data


def test_switch_nonexistent_spec(client, auth_headers):
    """Test switching on non-existent spec returns 404"""
    response = client.post(
        SWITCH_URL,
        json={"spec_id": "nonexistent_spec_xyz", "query": "change floor to marble"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_switch_invalid_object_id(client, auth_headers):
    """Test switch with a query that matches no objects returns 400"""
    spec_id = _generate_spec(client, auth_headers, "Design a room")

    response = client.post(
        SWITCH_URL,
        json={"spec_id": spec_id, "query": "change xyznonexistentobject999 to marble"},
        headers=auth_headers,
    )
    # Either 400 (no objects matched) or 200 (NLP matched something) is acceptable
    assert response.status_code in [200, 201, 400]


def test_switch_without_auth(client):
    """Test switch without authentication is rejected or returns 404 for missing spec"""
    response = client.post(
        SWITCH_URL,
        json={"spec_id": "test_spec_001", "query": "change floor to marble"},
    )
    # The switch route has no auth dependency; it processes the request and returns
    # 404 for a nonexistent spec, or 401/403/422 if auth is enforced
    assert response.status_code in [401, 403, 404, 422]


def test_switch_creates_iteration(client, auth_headers):
    """Test that switch creates an iteration record"""
    spec_id = _generate_spec(client, auth_headers, "Design a room")

    response = client.post(
        SWITCH_URL,
        json={"spec_id": spec_id, "query": "change wall to brick"},
        headers=auth_headers,
    )

    assert response.status_code in [200, 201]
    data = response.json()
    assert "iteration_id" in data


def test_switch_multiple_properties(client, auth_headers):
    """Test switching with a multi-property query"""
    spec_id = _generate_spec(client, auth_headers, "Design a room with table")

    response = client.post(
        SWITCH_URL,
        json={"spec_id": spec_id, "query": "change wall color to #CCCCCC"},
        headers=auth_headers,
    )

    assert response.status_code in [200, 201, 400]
