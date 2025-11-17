"""
Database connection module for the Distributed Compute Marketplace.

This module provides SQLAlchemy database connection handling with:
- Connection pooling for performance
- Transaction management via context managers
- FastAPI dependency injection support
- Environment-based configuration

Usage:
    from src.database.connection import get_db, transaction

    # FastAPI endpoint
    @app.get("/example")
    def example_endpoint(db = Depends(get_db)):
        user = db.query(User).first()
        return user

    # Manual transaction
    from src.database.connection import get_session
    SessionLocal = get_session()
    db = SessionLocal()
    with transaction(db):
        db.add(new_user)
        # Auto-commits on success, auto-rolls back on error
"""

import os
import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

# Setup logging
logger = logging.getLogger(__name__)


def get_database_url() -> str:
    """
    Get database URL from environment variables.

    Returns:
        Database URL string for SQLAlchemy connection

    Environment Variables:
        DATABASE_URL: Full PostgreSQL connection string
            Format: postgresql://user:password@host:port/database
            Default: postgresql://postgres:postgres@localhost:5432/compute_marketplace
    """
    default_url = "postgresql://postgres:postgres@localhost:5432/compute_marketplace"
    database_url = os.getenv("DATABASE_URL", default_url)

    logger.info(f"Using database URL: {database_url.split('@')[1] if '@' in database_url else 'default'}")

    return database_url


def get_engine():
    """
    Create and configure SQLAlchemy engine with connection pooling.

    Connection pool configuration:
    - Pool size: 5-20 connections (as per CLAUDE.md specification)
    - Pool recycle: 3600 seconds (1 hour) to prevent stale connections
    - Pool pre-ping: True to verify connections before use
    - Echo: False in production, can be enabled for debugging

    Returns:
        SQLAlchemy Engine instance

    Note:
        The engine is created once and reused. Connection pooling is handled
        automatically by SQLAlchemy.
    """
    database_url = get_database_url()

    # Create engine with connection pooling
    engine = create_engine(
        database_url,
        poolclass=pool.QueuePool,
        pool_size=5,           # Minimum pool size
        max_overflow=15,       # Maximum overflow (total max = 5 + 15 = 20)
        pool_recycle=3600,     # Recycle connections after 1 hour
        pool_pre_ping=True,    # Verify connections before using
        echo=False,            # Set to True for SQL query logging
        future=True,           # Use SQLAlchemy 2.0 style
    )

    logger.info("Database engine created with connection pooling (min=5, max=20)")

    return engine


def get_session() -> sessionmaker:
    """
    Get configured sessionmaker for creating database sessions.

    Returns:
        sessionmaker instance that can be called to create new sessions

    Usage:
        SessionLocal = get_session()
        db = SessionLocal()
        try:
            # Use db session
            user = db.query(User).first()
        finally:
            db.close()
    """
    engine = get_engine()

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False,  # Allow access to objects after commit
    )

    return SessionLocal


@contextmanager
def transaction(db: Session) -> Generator[Session, None, None]:
    """
    Context manager for database transactions.

    Automatically commits on success and rolls back on errors.
    This ensures atomicity for database operations.

    Args:
        db: SQLAlchemy Session instance

    Yields:
        The same Session instance

    Raises:
        SQLAlchemyError: Any database errors are re-raised after rollback

    Usage:
        db = SessionLocal()
        try:
            with transaction(db):
                db.add(new_user)
                db.add(new_node)
                # Both added atomically - commits if successful
        finally:
            db.close()

    Example with error handling:
        db = SessionLocal()
        try:
            with transaction(db):
                user = User(username="alice")
                db.add(user)
                raise ValueError("Oops!")  # Transaction auto-rolls back
        except ValueError:
            print("Transaction was rolled back")
        finally:
            db.close()
    """
    try:
        yield db
        db.commit()
        logger.debug("Transaction committed successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Transaction rolled back due to error: {type(e).__name__}: {e}")
        raise


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.

    Yields a database session and ensures it's closed after use.
    This is designed to be used with FastAPI's dependency injection.

    Yields:
        SQLAlchemy Session instance

    Usage:
        from fastapi import Depends
        from src.database.connection import get_db

        @app.get("/users")
        def list_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users

    Note:
        The session is automatically closed after the request completes,
        even if an exception occurs.
    """
    SessionLocal = get_session()
    db = SessionLocal()

    try:
        logger.debug("Database session created")
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error in request: {type(e).__name__}: {e}")
        raise
    finally:
        db.close()
        logger.debug("Database session closed")


# Singleton engine instance (created once, reused throughout app lifecycle)
_engine = None


def get_engine_singleton():
    """
    Get singleton engine instance.

    Creates engine on first call, returns cached instance on subsequent calls.
    This prevents creating multiple engine instances.

    Returns:
        SQLAlchemy Engine instance
    """
    global _engine
    if _engine is None:
        _engine = get_engine()
    return _engine


def close_db_connections():
    """
    Close all database connections.

    Useful for cleanup during testing or application shutdown.
    Disposes the engine and all connections in the pool.
    """
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
        logger.info("All database connections closed")
