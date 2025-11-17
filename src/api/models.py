"""
Pydantic models for API request/response validation.

These models define the data structures for API endpoints and provide
automatic validation, serialization, and documentation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    """
    Model for user registration requests.

    Validates:
    - Username: 3-50 characters
    - Email: Valid email format
    - Password: Minimum 8 characters
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username (3-50 characters)",
        examples=["alice"]
    )

    email: EmailStr = Field(
        ...,
        description="Valid email address",
        examples=["alice@example.com"]
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (minimum 8 characters)",
        examples=["SecurePassword123!"]
    )

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password meets security requirements.

        Requirements:
        - Minimum 8 characters
        - Not a common weak password

        Args:
            v: Password string to validate

        Returns:
            Validated password

        Raises:
            ValueError: If password is too weak
        """
        # Check minimum length (also enforced by Field)
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Check for common weak passwords
        weak_passwords = [
            "password", "12345678", "qwerty", "abc123",
            "password123", "admin", "letmein", "welcome"
        ]

        if v.lower() in weak_passwords:
            raise ValueError("Password is too common - please choose a stronger password")

        return v

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """
        Validate username format.

        Args:
            v: Username to validate

        Returns:
            Validated username

        Raises:
            ValueError: If username format is invalid
        """
        # Remove whitespace
        v = v.strip()

        # Check not empty after stripping
        if not v:
            raise ValueError("Username cannot be empty or whitespace only")

        return v


class UserLogin(BaseModel):
    """
    Model for user login requests.

    Simple username/password authentication.
    Returns API key on successful login.
    """

    username: str = Field(
        ...,
        description="Username",
        examples=["alice"]
    )

    password: str = Field(
        ...,
        description="Password",
        examples=["SecurePassword123!"]
    )


class UserResponse(BaseModel):
    """
    Model for user data responses.

    This model is used for all user data returned by the API.
    It excludes sensitive fields like password_hash.

    Note: api_key is only included in registration/login responses,
    not in general user data queries.
    """

    id: int = Field(
        ...,
        description="Unique user ID",
        examples=[1]
    )

    username: str = Field(
        ...,
        description="Username",
        examples=["alice"]
    )

    email: EmailStr = Field(
        ...,
        description="Email address",
        examples=["alice@example.com"]
    )

    api_key: Optional[str] = Field(
        None,
        description="API key for authentication (only returned on registration/login)",
        examples=["sk_test_abc123xyz789"]
    )

    credit_balance: int = Field(
        ...,
        description="Current credit balance",
        examples=[100]
    )

    created_at: datetime = Field(
        ...,
        description="Account creation timestamp",
        examples=["2025-11-17T12:00:00Z"]
    )

    # Pydantic v2 configuration
    model_config = {
        "from_attributes": True,  # Enable ORM mode for SQLAlchemy models
        "json_schema_extra": {
            "example": {
                "id": 1,
                "username": "alice",
                "email": "alice@example.com",
                "api_key": "sk_test_abc123xyz789",
                "credit_balance": 100,
                "created_at": "2025-11-17T12:00:00Z"
            }
        }
    }
