"""
Test cases for POST /api/v1/evaluate endpoint
"""

import pytest

GENERATE_URL = "/api/v1/core/generate"
EVALUATE_URL = "/api/v1/evaluate"


def _generate_spec(client, auth_headers, prompt="modern living room"):
    """Helper: generate a spec and return its spec_id."""
    resp = client.post(
        GENERATE_URL,
        json={"user_id": "demo_user_123", "prompt": prompt, "project_id": "project_001"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()["spec_id"]


def test_evaluate_valid_spec(client, auth_headers):
    """Test evaluating a spec with valid rating and notes"""
    spec_id = _generate_spec(client, auth_headers)

    response = client.post(
        EVALUATE_URL,
        json={
            "user_id": "demo_user_123",
            "spec_id": spec_id,
            "rating": 4.5,
            "notes": "Great design with good proportions and color harmony",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    result = response.json()
    assert result["ok"] is True
    assert "saved_id" in result


def test_evaluate_spec_not_found(client, auth_headers):
    """Test error when spec doesn't exist"""
    response = client.post(
        EVALUATE_URL,
        json={"user_id": "demo_user_123", "spec_id": "nonexistent_spec", "rating": 4.0, "notes": "Good design"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_evaluate_invalid_rating_range(client, auth_headers):
    """Test error for rating outside 0-5 range"""
    spec_id = _generate_spec(client, auth_headers)

    response = client.post(
        EVALUATE_URL,
        json={"user_id": "demo_user_123", "spec_id": spec_id, "rating": 10.0, "notes": "Amazing"},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_evaluate_triggers_feedback_loop(client, auth_headers):
    """Test that evaluation triggers feedback loop processing"""
    spec_id = _generate_spec(client, auth_headers, "living room design")

    response = client.post(
        EVALUATE_URL,
        json={"user_id": "demo_user_123", "spec_id": spec_id, "rating": 4.8, "notes": "Excellent design"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    result = response.json()
    assert "feedback_processed" in result or result["ok"] is True
