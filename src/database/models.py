"""
SQLAlchemy ORM models for the Distributed Compute Marketplace.

These models map to the database tables defined in schema.sql.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, TIMESTAMP, ARRAY
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

# Base class for all models
Base = declarative_base()


class User(Base):
    """
    User model for authentication and credit management.

    Maps to the 'users' table in PostgreSQL.

    Attributes:
        id: Unique user ID (primary key)
        username: Unique username (3-50 characters)
        email: Unique email address
        password_hash: Bcrypt hashed password
        api_key: Unique API key for authentication
        credit_balance: Current credit balance (default: 100)
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = 'users'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # User credentials
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    api_key = Column(String(64), unique=True, nullable=False, index=True)

    # Credit system
    credit_balance = Column(Integer, nullable=False, default=100)

    # Timestamps
    created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now()
    )
    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    def __repr__(self) -> str:
        """
        String representation for debugging.

        Returns:
            Human-readable string representation of User
        """
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    def to_dict(self) -> dict:
        """
        Convert User to dictionary (excludes password_hash for security).

        Returns:
            Dictionary representation of User
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'credit_balance': self.credit_balance,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
