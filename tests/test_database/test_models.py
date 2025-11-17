"""
Tests for SQLAlchemy database models.

Following TDD: These tests are written BEFORE implementation.
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError


class TestUserModel:
    """Test suite for User ORM model."""

    def test_user_can_be_created(self, db_session):
        """Test that a User can be created and saved to database."""
        from src.database.models import User

        user = User(
            username="alice",
            email="alice@example.com",
            password_hash="hashed_password_123",
            api_key="test_api_key_123"
        )

        db_session.add(user)
        db_session.commit()

        # Should have an ID after commit
        assert user.id is not None
        assert user.username == "alice"
        assert user.email == "alice@example.com"

    def test_user_can_be_queried(self, db_session):
        """Test that a User can be queried from database."""
        from src.database.models import User

        # Create user
        user = User(
            username="bob",
            email="bob@example.com",
            password_hash="hashed_password_456",
            api_key="test_api_key_456"
        )
        db_session.add(user)
        db_session.commit()

        # Query user
        queried_user = db_session.query(User).filter_by(username="bob").first()

        assert queried_user is not None
        assert queried_user.username == "bob"
        assert queried_user.email == "bob@example.com"

    def test_username_must_be_unique(self, db_session):
        """Test that duplicate usernames are rejected."""
        from src.database.models import User

        # Create first user
        user1 = User(
            username="alice",
            email="alice1@example.com",
            password_hash="hash1",
            api_key="key1"
        )
        db_session.add(user1)
        db_session.commit()

        # Try to create second user with same username
        user2 = User(
            username="alice",  # Duplicate
            email="alice2@example.com",
            password_hash="hash2",
            api_key="key2"
        )
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_email_must_be_unique(self, db_session):
        """Test that duplicate emails are rejected."""
        from src.database.models import User

        # Create first user
        user1 = User(
            username="alice",
            email="alice@example.com",
            password_hash="hash1",
            api_key="key1"
        )
        db_session.add(user1)
        db_session.commit()

        # Try to create second user with same email
        user2 = User(
            username="bob",
            email="alice@example.com",  # Duplicate
            password_hash="hash2",
            api_key="key2"
        )
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_api_key_must_be_unique(self, db_session):
        """Test that duplicate API keys are rejected."""
        from src.database.models import User

        # Create first user
        user1 = User(
            username="alice",
            email="alice@example.com",
            password_hash="hash1",
            api_key="same_key"
        )
        db_session.add(user1)
        db_session.commit()

        # Try to create second user with same API key
        user2 = User(
            username="bob",
            email="bob@example.com",
            password_hash="hash2",
            api_key="same_key"  # Duplicate
        )
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_has_default_credit_balance(self, db_session):
        """Test that new users have default credit balance of 100."""
        from src.database.models import User

        user = User(
            username="alice",
            email="alice@example.com",
            password_hash="hash",
            api_key="key"
        )
        db_session.add(user)
        db_session.commit()

        # Should have default credit balance
        assert user.credit_balance == 100

    def test_user_timestamps_auto_populate(self, db_session):
        """Test that created_at and updated_at auto-populate."""
        from src.database.models import User

        user = User(
            username="alice",
            email="alice@example.com",
            password_hash="hash",
            api_key="key"
        )
        db_session.add(user)
        db_session.commit()

        # Timestamps should be set
        assert user.created_at is not None
        assert user.updated_at is not None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_user_repr_method_exists(self, db_session):
        """Test that User has a __repr__ method for debugging."""
        from src.database.models import User

        user = User(
            username="alice",
            email="alice@example.com",
            password_hash="hash",
            api_key="key"
        )

        # Should have a useful repr
        repr_str = repr(user)
        assert "alice" in repr_str
        assert "User" in repr_str
