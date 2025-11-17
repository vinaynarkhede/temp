"""
Pytest configuration and shared fixtures.

This file provides fixtures that can be used across all test files.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool


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

    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

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


@pytest.fixture(scope="function")
def client(db_session):
    """
    Provide a FastAPI test client with database session override.

    This fixture creates a test client and overrides the get_db dependency
    to use the test database session.

    Args:
        db_session: Database session fixture

    Yields:
        FastAPI TestClient instance
    """
    # Import here to avoid circular imports
    from src.api.main import app
    from src.database.connection import get_db

    # Override the get_db dependency to use test database
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Session cleanup handled by db_session fixture

    app.dependency_overrides[get_db] = override_get_db

    # Create test client
    test_client = TestClient(app)

    yield test_client

    # Clear overrides after test
    app.dependency_overrides.clear()
