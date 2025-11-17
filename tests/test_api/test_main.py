"""
Tests for FastAPI main application.

Tests CORS, error handlers, and health check.
"""

import pytest
from fastapi.testclient import TestClient


class TestFastAPIApp:
    """Test suite for FastAPI application setup."""

    def test_app_starts_successfully(self, client):
        """Test that the FastAPI app starts and responds."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_endpoint(self, client):
        """Test that health check endpoint returns correct data."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        # Send request with Origin header to trigger CORS
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})

        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers

    def test_404_returns_proper_json(self, client):
        """Test that 404 errors return JSON response."""
        response = client.get("/nonexistent-endpoint")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_openapi_docs_accessible(self, client):
        """Test that OpenAPI documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

        response = client.get("/redoc")
        assert response.status_code == 200

    def test_openapi_json_accessible(self, client):
        """Test that OpenAPI JSON schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
