"""
SQLAlchemy ORM models for the Distributed Compute Marketplace.

These models map to the database tables defined in schema.sql.
"""

from datetime import datetime
import json
from typing import Any
from sqlalchemy import Column, Integer, String, Float, Boolean, TIMESTAMP, ARRAY, ForeignKey, Text, TypeDecorator, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func


class IntegerArray(TypeDecorator):
    """
    Custom type for storing integer arrays.

    Uses native PostgreSQL ARRAY type in production,
    falls back to JSON-encoded string for SQLite (testing).
    """
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.ARRAY(Integer))
        else:
            return dialect.type_descriptor(String(255))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        else:
            # For SQLite, store as JSON string
            return json.dumps(value) if value else None

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        else:
            # For SQLite, parse JSON string
            return json.loads(value) if value else None

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


class Node(Base):
    """
    Node model representing compute resources offered by users.

    Maps to the 'nodes' table in PostgreSQL.

    Attributes:
        id: Unique node ID (primary key)
        owner_id: Foreign key to users table
        name: Human-readable node name
        tailscale_ip: Tailscale VPN IP address
        cpu_cores: Number of CPU cores available
        ram_gb: RAM available in gigabytes
        storage_gb: Storage available in gigabytes
        status: Node status (online/offline/maintenance)
        last_heartbeat: Last heartbeat timestamp
        created_at: Node registration timestamp
    """

    __tablename__ = 'nodes'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Owner relationship
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Node details
    name = Column(String(100), nullable=False)
    tailscale_ip = Column(String(45), nullable=False)

    # Resource specs
    cpu_cores = Column(Integer, nullable=False)
    ram_gb = Column(Float, nullable=False)
    storage_gb = Column(Float, nullable=False)

    # Status tracking
    status = Column(String(20), nullable=False, default='offline')
    last_heartbeat = Column(TIMESTAMP, nullable=True)

    # Timestamps
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Node(id={self.id}, name='{self.name}', status='{self.status}')>"


class ResourceOffer(Base):
    """
    ResourceOffer model for marketplace listings.

    Maps to the 'resource_offers' table in PostgreSQL.

    Attributes:
        id: Unique offer ID (primary key)
        node_id: Foreign key to nodes table
        cpu_cores_available: CPU cores offered
        ram_gb_available: RAM offered in gigabytes
        storage_gb_available: Storage offered in gigabytes
        offer_type: 'paid' or 'free'
        approval_policy: 'auto_all', 'auto_friends', or 'manual'
        trusted_users: Array of user IDs for auto-approval
        active: Whether offer is currently active
        created_at: Offer creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = 'resource_offers'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Node relationship
    node_id = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'), nullable=False)

    # Available resources
    cpu_cores_available = Column(Integer, nullable=False)
    ram_gb_available = Column(Float, nullable=False)
    storage_gb_available = Column(Float, nullable=False)

    # Offer configuration
    offer_type = Column(String(20), nullable=False)
    approval_policy = Column(String(20), nullable=False, default='manual')
    trusted_users = Column(IntegerArray, nullable=True)

    # Status
    active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<ResourceOffer(id={self.id}, node_id={self.node_id}, type='{self.offer_type}')>"


class Job(Base):
    """
    Job model representing compute jobs submitted by users.

    Maps to the 'jobs' table in PostgreSQL.

    Attributes:
        id: Unique job ID (primary key)
        owner_id: Foreign key to users table
        docker_image: Docker image to run
        total_chunks: Number of chunks to split job into
        completed_chunks: Number of chunks completed
        status: Job status (pending/running/completed/failed)
        priority: Job priority (1=highest, 10=lowest)
        cpu_cores_per_chunk: CPU cores needed per chunk
        ram_gb_per_chunk: RAM needed per chunk in gigabytes
        estimated_duration_hours: Estimated runtime in hours
        created_at: Job submission timestamp
        completed_at: Job completion timestamp
    """

    __tablename__ = 'jobs'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Owner relationship
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Job configuration
    docker_image = Column(String(255), nullable=False)
    total_chunks = Column(Integer, nullable=False)
    completed_chunks = Column(Integer, nullable=False, default=0)

    # Status and priority
    status = Column(String(20), nullable=False, default='pending')
    priority = Column(Integer, nullable=False, default=5)

    # Resource requirements per chunk
    cpu_cores_per_chunk = Column(Integer, nullable=False)
    ram_gb_per_chunk = Column(Float, nullable=False)

    # Estimates
    estimated_duration_hours = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    completed_at = Column(TIMESTAMP, nullable=True)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Job(id={self.id}, status='{self.status}', chunks={self.completed_chunks}/{self.total_chunks})>"


class JobChunk(Base):
    """
    JobChunk model representing individual task units for fault tolerance.

    Maps to the 'job_chunks' table in PostgreSQL.

    Attributes:
        id: Unique chunk ID (primary key)
        job_id: Foreign key to jobs table
        chunk_number: Chunk number within job (0-indexed)
        assigned_node_id: Foreign key to nodes table (nullable)
        status: Chunk status (pending/running/completed/failed)
        input_data: Input data for chunk (JSON or S3 path)
        output_data: Output data from chunk (JSON or S3 path)
        started_at: Chunk start timestamp
        completed_at: Chunk completion timestamp
        retry_count: Number of times chunk has been retried
    """

    __tablename__ = 'job_chunks'
    __table_args__ = (
        UniqueConstraint('job_id', 'chunk_number', name='uq_job_chunk'),
    )

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Job relationship
    job_id = Column(Integer, ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    chunk_number = Column(Integer, nullable=False, unique=False)

    # Node assignment
    assigned_node_id = Column(Integer, ForeignKey('nodes.id', ondelete='SET NULL'), nullable=True)

    # Status
    status = Column(String(20), nullable=False, default='pending')

    # Data
    input_data = Column(Text, nullable=True)
    output_data = Column(Text, nullable=True)

    # Timestamps
    started_at = Column(TIMESTAMP, nullable=True)
    completed_at = Column(TIMESTAMP, nullable=True)

    # Retry tracking
    retry_count = Column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<JobChunk(id={self.id}, job_id={self.job_id}, chunk={self.chunk_number}, status='{self.status}')>"


class CreditTransaction(Base):
    """
    CreditTransaction model for audit trail of credit transfers.

    Maps to the 'credit_transactions' table in PostgreSQL.

    Attributes:
        id: Unique transaction ID (primary key)
        from_user_id: Foreign key to users table (sender, nullable)
        to_user_id: Foreign key to users table (receiver, nullable)
        amount: Credit amount transferred
        transaction_type: Type of transaction
        job_id: Foreign key to jobs table (nullable)
        created_at: Transaction timestamp
    """

    __tablename__ = 'credit_transactions'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # User relationships (nullable for system transactions)
    from_user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    to_user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # Transaction details
    amount = Column(Integer, nullable=False)
    transaction_type = Column(String(50), nullable=True)

    # Job relationship (nullable)
    job_id = Column(Integer, ForeignKey('jobs.id', ondelete='SET NULL'), nullable=True)

    # Timestamp
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<CreditTransaction(id={self.id}, amount={self.amount}, type='{self.transaction_type}')>"
