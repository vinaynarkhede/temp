"""
Tests for Pydantic API models.

Following TDD: These tests are written BEFORE implementation.
They define the expected validation behavior for API models.
"""

import pytest
from pydantic import ValidationError


class TestUserRegisterModel:
    """Test suite for UserRegister Pydantic model."""

    def test_valid_user_registration_data_passes(self):
        """Test that valid registration data passes validation."""
        from src.api.models import UserRegister

        user_data = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "SecurePassword123!"
        }

        user = UserRegister(**user_data)

        assert user.username == "alice"
        assert user.email == "alice@example.com"
        assert user.password == "SecurePassword123!"

    def test_invalid_email_rejected(self):
        """Test that invalid email format is rejected."""
        from src.api.models import UserRegister

        invalid_emails = [
            "not-an-email",
            "missing@domain",
            "@example.com",
            "user@",
            "user @example.com",
        ]

        for invalid_email in invalid_emails:
            with pytest.raises(ValidationError) as exc_info:
                UserRegister(
                    username="alice",
                    email=invalid_email,
                    password="SecurePassword123!"
                )
            # Should have validation error for email field
            assert 'email' in str(exc_info.value).lower()

    def test_weak_password_rejected(self):
        """Test that weak passwords are rejected."""
        from src.api.models import UserRegister

        weak_passwords = [
            "short",       # Too short
            "12345678",    # Only numbers
            "password",    # Too common
            "abc",         # Too short
        ]

        for weak_password in weak_passwords:
            with pytest.raises(ValidationError) as exc_info:
                UserRegister(
                    username="alice",
                    email="alice@example.com",
                    password=weak_password
                )
            # Should have validation error for password field
            assert 'password' in str(exc_info.value).lower()

    def test_missing_required_field_rejected(self):
        """Test that missing required fields are rejected."""
        from src.api.models import UserRegister

        # Missing username
        with pytest.raises(ValidationError):
            UserRegister(
                email="alice@example.com",
                password="SecurePassword123!"
            )

        # Missing email
        with pytest.raises(ValidationError):
            UserRegister(
                username="alice",
                password="SecurePassword123!"
            )

        # Missing password
        with pytest.raises(ValidationError):
            UserRegister(
                username="alice",
                email="alice@example.com"
            )

    def test_username_too_short_rejected(self):
        """Test that usernames that are too short are rejected."""
        from src.api.models import UserRegister

        with pytest.raises(ValidationError):
            UserRegister(
                username="ab",  # Less than 3 characters
                email="alice@example.com",
                password="SecurePassword123!"
            )

    def test_username_too_long_rejected(self):
        """Test that usernames that are too long are rejected."""
        from src.api.models import UserRegister

        with pytest.raises(ValidationError):
            UserRegister(
                username="a" * 51,  # More than 50 characters
                email="alice@example.com",
                password="SecurePassword123!"
            )


class TestUserLoginModel:
    """Test suite for UserLogin Pydantic model."""

    def test_valid_login_data_passes(self):
        """Test that valid login data passes validation."""
        from src.api.models import UserLogin

        login_data = {
            "username": "alice",
            "password": "SecurePassword123!"
        }

        login = UserLogin(**login_data)

        assert login.username == "alice"
        assert login.password == "SecurePassword123!"

    def test_missing_username_rejected(self):
        """Test that missing username is rejected."""
        from src.api.models import UserLogin

        with pytest.raises(ValidationError):
            UserLogin(password="SecurePassword123!")

    def test_missing_password_rejected(self):
        """Test that missing password is rejected."""
        from src.api.models import UserLogin

        with pytest.raises(ValidationError):
            UserLogin(username="alice")


class TestUserResponseModel:
    """Test suite for UserResponse Pydantic model."""

    def test_user_response_does_not_expose_password(self):
        """Test that UserResponse does not include password fields."""
        from src.api.models import UserResponse

        # Model should not have password or password_hash fields
        assert 'password' not in UserResponse.model_fields
        assert 'password_hash' not in UserResponse.model_fields

    def test_user_response_includes_required_fields(self):
        """Test that UserResponse includes all necessary user data."""
        from src.api.models import UserResponse

        # Should have these fields
        required_fields = ['id', 'username', 'email', 'credit_balance', 'created_at']

        for field in required_fields:
            assert field in UserResponse.model_fields, f"Missing field: {field}"

    def test_user_response_includes_api_key(self):
        """Test that UserResponse includes api_key (for registration response)."""
        from src.api.models import UserResponse

        # api_key should be optional (only returned on registration/login)
        assert 'api_key' in UserResponse.model_fields

    def test_valid_user_response_creation(self):
        """Test creating a valid UserResponse instance."""
        from src.api.models import UserResponse
        from datetime import datetime

        user_data = {
            "id": 1,
            "username": "alice",
            "email": "alice@example.com",
            "api_key": "test_api_key_123",
            "credit_balance": 100,
            "created_at": datetime.now()
        }

        user = UserResponse(**user_data)

        assert user.id == 1
        assert user.username == "alice"
        assert user.email == "alice@example.com"
        assert user.api_key == "test_api_key_123"
        assert user.credit_balance == 100

    def test_user_response_with_orm_mode(self):
        """Test that UserResponse can be created from ORM models."""
        from src.api.models import UserResponse

        # Check if model has orm_mode enabled (Pydantic v1) or from_attributes (Pydantic v2)
        config = UserResponse.model_config

        # Should support ORM model conversion
        assert config.get('from_attributes', False) is True, \
            "UserResponse should have from_attributes=True to work with SQLAlchemy models"
