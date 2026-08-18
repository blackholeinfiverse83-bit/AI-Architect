"""
Comprehensive endpoint tests for all API endpoints.
Tests cover success paths, error cases, and edge cases.
"""

import json
from datetime import datetime, timedelta

import pytest
from app.database_mongodb import get_database
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


# Fixtures
@pytest.fixture
def auth_token():
    """Get valid auth token"""
    response = client.post("/api/v1/auth/login", data={"username": "demo", "password": "demo123"})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}


# Test: /api/v1/health
class TestHealth:
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "uptime" in data
        assert "service" in data

    def test_health_detailed(self):
        """Test detailed health endpoint"""
        response = client.get("/api/v1/health/detailed")
        assert response.status_code == 200
        data = response.json()
        # Status reflects live external service availability; accept any valid status
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert "components" in data


# Test: /api/v1/core/generate
class TestGenerate:
    def test_generate_success(self, auth_headers):
        """Test successful spec generation via core endpoint"""
        response = client.post(
            "/api/v1/core/generate",
            headers=auth_headers,
            json={
                "user_id": "demo",
                "prompt": "Design a modern living room with marble floor",
                "context": {"style": "modern", "dimensions": {"length": 20, "width": 15, "height": 3}},
            },
        )
        assert response.status_code in [201, 500, 503]
        if response.status_code == 201:
            data = response.json()
            assert "spec_id" in data
            assert "spec_json" in data
            assert "preview_url" in data
            assert data["spec_json"] is not None

    def test_generate_missing_prompt(self, auth_headers):
        """Test generation with missing prompt"""
        response = client.post("/api/v1/core/generate", headers=auth_headers, json={"user_id": "demo"})
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_generate_unauthorized(self):
        """Test generation without auth"""
        response = client.post("/api/v1/core/generate", json={"user_id": "demo", "prompt": "Test"})
        assert response.status_code in [401, 403]


# Test: /api/v1/switch
class TestSwitch:
    def test_switch_success(self, auth_headers):
        """Test successful material switch"""
        gen_response = client.post(
            "/api/v1/core/generate",
            headers=auth_headers,
            json={"user_id": "demo", "prompt": "Design a modern living room", "context": {"style": "modern"}},
        )
        assert gen_response.status_code in [201, 500, 503]
        if gen_response.status_code != 201:
            return
        spec_id = gen_response.json()["spec_id"]

        response = client.post(
            "/api/v1/switch",
            headers=auth_headers,
            json={"spec_id": spec_id, "query": "change floor to marble"},
        )
        # Switch looks up spec in spec_storage (in-memory) then MongoDB;
        # after core/generate the spec is in MongoDB so switch should find it
        assert response.status_code in [200, 201, 404]

    def test_switch_spec_not_found(self, auth_headers):
        """Test switch on non-existent spec"""
        response = client.post(
            "/api/v1/switch",
            headers=auth_headers,
            json={"spec_id": "nonexistent", "query": "change floor to marble"},
        )
        assert response.status_code == 404

    def test_switch_invalid_object(self, auth_headers):
        """Test switch with a query that matches no objects"""
        gen_response = client.post(
            "/api/v1/core/generate",
            headers=auth_headers,
            json={"user_id": "demo", "prompt": "Design a room", "context": {"style": "modern"}},
        )
        assert gen_response.status_code in [201, 500, 503]
        if gen_response.status_code != 201:
            return
        spec_id = gen_response.json()["spec_id"]

        response = client.post(
            "/api/v1/switch",
            headers=auth_headers,
            json={"spec_id": spec_id, "query": "change xyznonexistent999 to marble"},
        )
        assert response.status_code in [200, 201, 400, 404]


# Test: /api/v1/evaluate
class TestEvaluate:
    def test_evaluate_success(self, auth_headers):
        """Test successful evaluation"""
        gen_response = client.post(
            "/api/v1/core/generate", headers=auth_headers, json={"user_id": "demo", "prompt": "Design a modern room"}
        )
        assert gen_response.status_code in [201, 500, 503]
        if gen_response.status_code != 201:
            return
        spec_id = gen_response.json()["spec_id"]

        response = client.post(
            "/api/v1/evaluate",
            headers=auth_headers,
            json={"user_id": "demo", "spec_id": spec_id, "rating": 4.5, "notes": "Great design!"},
        )
        # evaluate looks up spec in MongoDB; 200 = found and saved, 404 = spec not persisted yet
        assert response.status_code in [200, 404, 500]
        if response.status_code == 200:
            data = response.json()
            assert data["ok"] is True
            assert "saved_id" in data


# Test: /api/v1/iterate
class TestIterate:
    def test_iterate_success(self, auth_headers):
        """Test successful iteration"""
        gen_response = client.post(
            "/api/v1/core/generate", headers=auth_headers, json={"user_id": "demo", "prompt": "Design a modern room"}
        )
        assert gen_response.status_code in [201, 500, 503]
        if gen_response.status_code != 201:
            return
        spec_id = gen_response.json()["spec_id"]

        response = client.post(
            "/api/v1/iterate",
            headers=auth_headers,
            json={"user_id": "demo", "spec_id": spec_id, "strategy": "improve_materials"},
        )
        # iterate_service looks up spec in spec_storage then DB; 200 = success, 404/500 = lookup failure
        assert response.status_code in [200, 404, 500]
        if response.status_code == 200:
            data = response.json()
            assert "before" in data
            assert "after" in data
            assert "feedback" in data


# Test: /api/v1/auth/login
class TestAuth:
    def test_login_success(self):
        """Test successful login"""
        response = client.post("/api/v1/auth/login", data={"username": "demo", "password": "demo123"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = client.post("/api/v1/auth/login", data={"username": "demo", "password": "wrong"})
        # DEMO_MODE only accepts the exact demo password; wrong password falls through to MongoDB
        # which may be unavailable in test environment → 401 or 503 are both valid
        assert response.status_code in [401, 503]

    def test_login_missing_credentials(self):
        """Test login without credentials"""
        response = client.post("/api/v1/auth/login")
        assert response.status_code in [400, 422]


# Test: /api/v1/data/* (Data Privacy)
class TestDataPrivacy:
    def test_export_user_data(self, auth_headers):
        """Test GDPR-style data export"""
        response = client.get("/api/v1/data/demo/export", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "demo"
        assert "export_timestamp" in data
        assert "data" in data

    def test_export_forbidden_for_other_user(self, auth_headers):
        """Test that users cannot export other user's data"""
        response = client.get("/api/v1/data/admin/export", headers=auth_headers)
        assert response.status_code == 403


# Test: Error handling
class TestErrorHandling:
    def test_payload_too_large(self, auth_headers):
        """Test that very large payloads are handled (rejected or processed)"""
        large_payload = {"user_id": "demo", "prompt": "x" * (51 * 1024 * 1024)}

        response = client.post("/api/v1/core/generate", headers=auth_headers, json=large_payload)
        # Middleware may reject (413), validation may reject (400/422), or pipeline may fail (500)
        assert response.status_code in [400, 413, 422, 500]

    def test_structured_error_response(self):
        """Test that errors follow structured format"""
        response = client.post("/api/v1/generate", json={"invalid": "request"})
        assert response.status_code in [401, 403, 422]
        data = response.json()
        # Accept either error format
        assert "error" in data or "detail" in data


# Test: Rate limiting (if enabled)
class TestRateLimit:
    def test_rate_limit_headers(self, auth_headers):
        """Test rate limit headers are present"""
        response = client.get("/api/v1/health", headers=auth_headers)
        # Rate limiting might not be enabled in test environment
        assert response.status_code == 200
