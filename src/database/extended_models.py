"""Extended database models for new features."""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from src.database.models import Base


class NodeMetrics(Base):
    """Performance metrics for nodes."""
    __tablename__ = "node_metrics"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    jobs_completed = Column(Integer, default=0)
    jobs_failed = Column(Integer, default=0)
    avg_chunk_time_seconds = Column(Float, default=0.0)
    total_uptime_hours = Column(Float, default=0.0)
    failure_rate = Column(Float, default=0.0)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())


class UserPreference(Base):
    """User preferences for nodes and settings."""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    preferred_node_ids = Column(JSON, default=[])  # List of node IDs
    avoided_node_ids = Column(JSON, default=[])
    notification_email = Column(String(255))
    notification_webhook = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AuditLog(Base):
    """Audit trail for all API actions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(100), nullable=False)  # e.g., "submit_job", "delete_node"
    resource_type = Column(String(50))  # e.g., "job", "node", "offer"
    resource_id = Column(Integer)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    details = Column(JSON)  # Additional contextual data
    created_at = Column(DateTime, server_default=func.now(), index=True)


class JobTag(Base):
    """Tags for organizing jobs."""
    __tablename__ = "job_tags"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    tag = Column(String(50), nullable=False, index=True)


class ResourceBid(Base):
    """Bidding system for resources."""
    __tablename__ = "resource_bids"

    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, ForeignKey("resource_offers.id", ondelete="CASCADE"), nullable=False)
    bidder_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    max_price_per_hour = Column(Integer, nullable=False)
    duration_hours = Column(Float, nullable=False)
    status = Column(String(20), default="pending")  # pending, accepted, rejected
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime)


class NodeSchedule(Base):
    """Availability schedule for nodes."""
    __tablename__ = "node_schedules"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    available_from = Column(DateTime, nullable=False)
    available_until = Column(DateTime, nullable=False)
    recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(100))  # e.g., "weekly", "daily"


class JobCheckpoint(Base):
    """Checkpoints for long-running jobs."""
    __tablename__ = "job_checkpoints"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(Integer, ForeignKey("job_chunks.id", ondelete="CASCADE"))
    checkpoint_data = Column(Text)  # Serialized state or S3 path
    progress_percentage = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
