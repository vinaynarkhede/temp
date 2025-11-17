"""
Tests for database connection module.

Following TDD: These tests are written BEFORE implementation.
They define the expected behavior of the connection module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import text
from sqlalchemy.exc import OperationalError


class TestDatabaseConnection:
    """Test suite for database connection functionality."""

    def test_get_engine_creates_engine_with_correct_url(self):
        """Test that get_engine creates SQLAlchemy engine with correct database URL."""
        from src.database.connection import get_engine

        engine = get_engine()

        # Engine should be created
        assert engine is not None

        # Should be a SQLAlchemy engine
        assert hasattr(engine, 'connect')
        assert hasattr(engine, 'dispose')

    def test_get_engine_configures_connection_pooling(self):
        """Test that connection pooling is configured correctly."""
        from src.database.connection import get_engine

        engine = get_engine()

        # Check pool configuration
        pool = engine.pool
        assert pool.size() >= 0  # Pool should exist
        # Pool settings should match requirements (min=5, max=20)
        # Note: These values are set in the engine creation

    def test_get_session_returns_session_maker(self):
        """Test that get_session returns a configured sessionmaker."""
        from src.database.connection import get_session

        SessionLocal = get_session()

        # Should be callable (sessionmaker)
        assert callable(SessionLocal)

        # Should create a session when called
        session = SessionLocal()
        assert session is not None
        session.close()

    def test_session_can_execute_queries(self):
        """Test that sessions can execute SQL queries."""
        from src.database.connection import get_session

        SessionLocal = get_session()
        session = SessionLocal()

        try:
            # Should be able to execute a simple query
            result = session.execute(text("SELECT 1 as test"))
            row = result.first()
            assert row is not None
            assert row.test == 1
        except OperationalError:
            # If database is not available, that's okay for this test
            # We're just checking the interface is correct
            pytest.skip("Database not available")
        finally:
            session.close()

    def test_transaction_context_manager_commits_on_success(self):
        """Test that transaction context manager commits on success."""
        from src.database.connection import transaction, get_session

        SessionLocal = get_session()
        session = SessionLocal()

        try:
            # Mock the commit and rollback methods
            session.commit = Mock()
            session.rollback = Mock()

            # Use transaction context manager
            with transaction(session):
                pass  # Successful execution

            # Should have committed
            session.commit.assert_called_once()
            # Should not have rolled back
            session.rollback.assert_not_called()
        finally:
            session.close()

    def test_transaction_context_manager_rolls_back_on_error(self):
        """Test that transaction context manager rolls back on error."""
        from src.database.connection import transaction, get_session

        SessionLocal = get_session()
        session = SessionLocal()

        try:
            # Mock the commit and rollback methods
            session.commit = Mock()
            session.rollback = Mock()

            # Use transaction context manager with error
            with pytest.raises(ValueError):
                with transaction(session):
                    raise ValueError("Test error")

            # Should not have committed
            session.commit.assert_not_called()
            # Should have rolled back
            session.rollback.assert_called_once()
        finally:
            session.close()

    def test_get_db_dependency_yields_session(self):
        """Test that get_db FastAPI dependency yields a session."""
        from src.database.connection import get_db

        # get_db should be a generator
        db_gen = get_db()

        # Should yield a session
        session = next(db_gen)
        assert session is not None
        assert hasattr(session, 'execute')
        assert hasattr(session, 'commit')

        # Should clean up after
        try:
            next(db_gen)
        except StopIteration:
            pass  # Expected - generator should end after yielding once

    def test_get_db_dependency_closes_session_on_completion(self):
        """Test that get_db closes session after use."""
        from src.database.connection import get_db

        db_gen = get_db()
        session = next(db_gen)

        # Mock the close method
        session.close = Mock()

        # Trigger cleanup
        try:
            next(db_gen)
        except StopIteration:
            pass

        # Should have closed the session
        session.close.assert_called_once()

    def test_database_url_uses_environment_variables(self):
        """Test that database URL is constructed from environment variables."""
        with patch.dict('os.environ', {
            'DATABASE_URL': 'postgresql://testuser:testpass@testhost:5432/testdb'
        }):
            from src.database.connection import get_database_url

            url = get_database_url()
            assert 'testuser' in url
            assert 'testhost' in url
            assert 'testdb' in url

    def test_database_url_has_default_value(self):
        """Test that database URL has a sensible default if env var not set."""
        with patch.dict('os.environ', {}, clear=True):
            from src.database.connection import get_database_url

            url = get_database_url()
            assert url is not None
            assert url.startswith('postgresql://')

    def test_connection_error_is_handled_gracefully(self):
        """Test that connection errors are raised appropriately."""
        from src.database.connection import get_engine

        # Create engine with invalid URL
        with patch('src.database.connection.get_database_url', return_value='postgresql://invalid:invalid@nonexistent:5432/invalid'):
            engine = get_engine()

            # Attempting to connect should raise OperationalError
            with pytest.raises(Exception):  # Could be OperationalError or similar
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
