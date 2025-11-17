"""
Tests for authentication API endpoints.

Following TDD: These tests are written BEFORE implementation.
"""

import pytest
from fastapi.testclient import TestClient


class TestUserRegistration:
    """Test suite for user registration endpoint."""

    def test_valid_registration_succeeds(self, client, db_session):
        """Test that valid registration data creates a user and returns API key."""
        response = client.post("/auth/register", json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "SecurePassword123!"
        })

        assert response.status_code == 201
        data = response.json()

        # Should return user data with API key
        assert "id" in data
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert "api_key" in data
        assert data["credit_balance"] == 100

        # Should NOT expose password
        assert "password" not in data
        assert "password_hash" not in data

    def test_registration_hashes_password(self, client, db_session):
        """Test that password is hashed, not stored in plain text."""
        from src.database.models import User

        response = client.post("/auth/register", json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "MyPassword123!"
        })

        assert response.status_code == 201

        # Check database
        user = db_session.query(User).filter_by(username="bob").first()
        assert user is not None
        # Password hash should start with $2b$ (bcrypt)
        assert user.password_hash.startswith('$2b$')
        # Should not be the plain password
        assert user.password_hash != "MyPassword123!"

    def test_registration_generates_api_key(self, client, db_session):
        """Test that registration generates a unique API key."""
        from src.database.models import User

        response = client.post("/auth/register", json={
            "username": "charlie",
            "email": "charlie@example.com",
            "password": "SecurePassword123!"
        })

        assert response.status_code == 201
        data = response.json()

        # API key should be 64 characters
        assert len(data["api_key"]) == 64

        # Check database
        user = db_session.query(User).filter_by(username="charlie").first()
        assert user.api_key == data["api_key"]

    def test_duplicate_username_rejected(self, client, db_session):
        """Test that duplicate usernames are rejected."""
        # Create first user
        client.post("/auth/register", json={
            "username": "alice",
            "email": "alice1@example.com",
            "password": "Password123!"
        })

        # Try to create second user with same username
        response = client.post("/auth/register", json={
            "username": "alice",  # Duplicate
            "email": "alice2@example.com",
            "password": "Password123!"
        })

        assert response.status_code == 409  # Conflict
        assert "username" in response.json()["detail"].lower()

    def test_duplicate_email_rejected(self, client, db_session):
        """Test that duplicate emails are rejected."""
        # Create first user
        client.post("/auth/register", json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "Password123!"
        })

        # Try to create second user with same email
        response = client.post("/auth/register", json={
            "username": "bob",
            "email": "alice@example.com",  # Duplicate
            "password": "Password123!"
        })

        assert response.status_code == 409  # Conflict
        assert "email" in response.json()["detail"].lower()

    def test_invalid_email_rejected(self, client, db_session):
        """Test that invalid email format is rejected."""
        response = client.post("/auth/register", json={
            "username": "alice",
            "email": "not-an-email",
            "password": "SecurePassword123!"
        })

        assert response.status_code == 422  # Validation error

    def test_weak_password_rejected(self, client, db_session):
        """Test that weak passwords are rejected."""
        response = client.post("/auth/register", json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "weak"  # Too short
        })

        assert response.status_code == 422  # Validation error

    def test_missing_fields_rejected(self, client, db_session):
        """Test that missing required fields are rejected."""
        # Missing email
        response = client.post("/auth/register", json={
            "username": "alice",
            "password": "SecurePassword123!"
        })
        assert response.status_code == 422

        # Missing password
        response = client.post("/auth/register", json={
            "username": "alice",
            "email": "alice@example.com"
        })
        assert response.status_code == 422

    def test_user_starts_with_100_credits(self, client, db_session):
        """Test that new users start with 100 credits."""
        response = client.post("/auth/register", json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "SecurePassword123!"
        })

        assert response.status_code == 201
        assert response.json()["credit_balance"] == 100


class TestUserLogin:
    """Test suite for user login endpoint."""

    def test_valid_login_succeeds(self, client, db_session):
        """Test that valid credentials return API key."""
        # First register a user
        client.post("/auth/register", json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "SecurePassword123!"
        })

        # Then login
        response = client.post("/auth/login", json={
            "username": "alice",
            "password": "SecurePassword123!"
        })

        assert response.status_code == 200
        data = response.json()

        # Should return user data with API key
        assert "id" in data
        assert data["username"] == "alice"
        assert "api_key" in data
        assert len(data["api_key"]) == 64

    def test_login_with_incorrect_password_fails(self, client, db_session):
        """Test that incorrect password is rejected."""
        # Register user
        client.post("/auth/register", json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "CorrectPassword123!"
        })

        # Try to login with wrong password
        response = client.post("/auth/login", json={
            "username": "alice",
            "password": "WrongPassword456!"
        })

        assert response.status_code == 401
        assert "credentials" in response.json()["detail"].lower()

    def test_login_with_nonexistent_username_fails(self, client, db_session):
        """Test that non-existent username is rejected."""
        response = client.post("/auth/login", json={
            "username": "nonexistent",
            "password": "SomePassword123!"
        })

        assert response.status_code == 401
        assert "credentials" in response.json()["detail"].lower()

    def test_login_returns_same_api_key(self, client, db_session):
        """Test that login returns the existing API key (not a new one)."""
        # Register user
        reg_response = client.post("/auth/register", json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "SecurePassword123!"
        })
        original_api_key = reg_response.json()["api_key"]

        # Login
        login_response = client.post("/auth/login", json={
            "username": "alice",
            "password": "SecurePassword123!"
        })

        # Should return the SAME API key
        assert login_response.json()["api_key"] == original_api_key
