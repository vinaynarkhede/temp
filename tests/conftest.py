"""
Pytest configuration and shared fixtures.

This file provides fixtures that can be used across all test files.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Import Base from models (will be created)
# We'll import this after models are defined


@pytest.fixture(scope="function")
def db_session():
    """
    Provide a database session for testing.

    Creates an in-memory SQLite database for each test function.
    Automatically rolls back after each test to ensure isolation.

    Yields:
        SQLAlchemy Session instance
    """
    # Import here to avoid circular imports
    from src.database.models import Base

    # Create in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(engine)

    # Create session
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        # Drop all tables
        Base.metadata.drop_all(engine)
