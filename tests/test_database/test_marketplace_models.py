"""
Tests for marketplace-related SQLAlchemy models.

Following TDD: These tests are written BEFORE implementation.
Tests for Node, ResourceOffer, Job, JobChunk, and CreditTransaction models.
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError


class TestNodeModel:
    """Test suite for Node model."""

    def test_node_can_be_created(self, db_session):
        """Test that a node can be created with valid data."""
        from src.database.models import Node, User

        # Create a user first (nodes belong to users)
        user = User(
            username="alice",
            email="alice@example.com",
            password_hash="hashed_password",
            api_key="test_api_key_123"
        )
        db_session.add(user)
        db_session.flush()

        # Create a node
        node = Node(
            owner_id=user.id,
            name="Alice-Desktop",
            tailscale_ip="100.64.0.1",
            cpu_cores=8,
            ram_gb=16.0,
            storage_gb=500.0,
            status="online"
        )
        db_session.add(node)
        db_session.commit()

        assert node.id is not None
        assert node.owner_id == user.id
        assert node.name == "Alice-Desktop"
        assert node.tailscale_ip == "100.64.0.1"
        assert node.cpu_cores == 8
        assert node.ram_gb == 16.0
        assert node.status == "online"

    def test_node_has_default_status(self, db_session):
        """Test that node status defaults to 'offline'."""
        from src.database.models import Node, User

        user = User(
            username="bob",
            email="bob@example.com",
            password_hash="hashed",
            api_key="api_key_456"
        )
        db_session.add(user)
        db_session.flush()

        node = Node(
            owner_id=user.id,
            name="Bob-Laptop",
            tailscale_ip="100.64.0.2",
            cpu_cores=4,
            ram_gb=8.0,
            storage_gb=250.0
        )
        db_session.add(node)
        db_session.commit()

        assert node.status == "offline"

    def test_node_timestamps_auto_populate(self, db_session):
        """Test that created_at timestamp is automatically set."""
        from src.database.models import Node, User

        user = User(
            username="charlie",
            email="charlie@example.com",
            password_hash="hashed",
            api_key="api_key_789"
        )
        db_session.add(user)
        db_session.flush()

        node = Node(
            owner_id=user.id,
            name="Charlie-PC",
            tailscale_ip="100.64.0.3",
            cpu_cores=16,
            ram_gb=32.0,
            storage_gb=1000.0
        )
        db_session.add(node)
        db_session.commit()

        assert node.created_at is not None
        assert isinstance(node.created_at, datetime)

    def test_node_cascades_on_user_delete(self, db_session):
        """Test that nodes are deleted when their owner is deleted."""
        from src.database.models import Node, User

        user = User(
            username="dave",
            email="dave@example.com",
            password_hash="hashed",
            api_key="api_key_abc"
        )
        db_session.add(user)
        db_session.flush()

        node = Node(
            owner_id=user.id,
            name="Dave-Server",
            tailscale_ip="100.64.0.4",
            cpu_cores=32,
            ram_gb=64.0,
            storage_gb=2000.0
        )
        db_session.add(node)
        db_session.commit()

        node_id = node.id

        # Delete user
        db_session.delete(user)
        db_session.commit()

        # Node should be deleted (cascade)
        deleted_node = db_session.query(Node).filter_by(id=node_id).first()
        assert deleted_node is None


class TestResourceOfferModel:
    """Test suite for ResourceOffer model."""

    def test_resource_offer_can_be_created(self, db_session):
        """Test that a resource offer can be created."""
        from src.database.models import ResourceOffer, Node, User

        user = User(
            username="alice",
            email="alice@example.com",
            password_hash="hashed",
            api_key="api_key_1"
        )
        db_session.add(user)
        db_session.flush()

        node = Node(
            owner_id=user.id,
            name="Alice-Desktop",
            tailscale_ip="100.64.0.1",
            cpu_cores=8,
            ram_gb=16.0,
            storage_gb=500.0
        )
        db_session.add(node)
        db_session.flush()

        offer = ResourceOffer(
            node_id=node.id,
            cpu_cores_available=4,
            ram_gb_available=8.0,
            storage_gb_available=100.0,
            offer_type="paid"
        )
        db_session.add(offer)
        db_session.commit()

        assert offer.id is not None
        assert offer.node_id == node.id
        assert offer.cpu_cores_available == 4
        assert offer.offer_type == "paid"

    def test_resource_offer_has_default_approval_policy(self, db_session):
        """Test that approval_policy defaults to 'manual'."""
        from src.database.models import ResourceOffer, Node, User

        user = User(username="bob", email="bob@example.com", password_hash="h", api_key="k")
        db_session.add(user)
        db_session.flush()

        node = Node(
            owner_id=user.id,
            name="Bob-PC",
            tailscale_ip="100.64.0.2",
            cpu_cores=4,
            ram_gb=8.0,
            storage_gb=200.0
        )
        db_session.add(node)
        db_session.flush()

        offer = ResourceOffer(
            node_id=node.id,
            cpu_cores_available=2,
            ram_gb_available=4.0,
            storage_gb_available=50.0,
            offer_type="free"
        )
        db_session.add(offer)
        db_session.commit()

        assert offer.approval_policy == "manual"

    def test_resource_offer_has_default_active_true(self, db_session):
        """Test that active defaults to True."""
        from src.database.models import ResourceOffer, Node, User

        user = User(username="charlie", email="charlie@example.com", password_hash="h", api_key="k2")
        db_session.add(user)
        db_session.flush()

        node = Node(
            owner_id=user.id,
            name="Charlie-Laptop",
            tailscale_ip="100.64.0.3",
            cpu_cores=8,
            ram_gb=16.0,
            storage_gb=300.0
        )
        db_session.add(node)
        db_session.flush()

        offer = ResourceOffer(
            node_id=node.id,
            cpu_cores_available=4,
            ram_gb_available=8.0,
            storage_gb_available=100.0,
            offer_type="paid"
        )
        db_session.add(offer)
        db_session.commit()

        assert offer.active is True


class TestJobModel:
    """Test suite for Job model."""

    def test_job_can_be_created(self, db_session):
        """Test that a job can be created."""
        from src.database.models import Job, User

        user = User(username="alice", email="alice@example.com", password_hash="h", api_key="k")
        db_session.add(user)
        db_session.flush()

        job = Job(
            owner_id=user.id,
            docker_image="python:3.11-slim",
            total_chunks=4,
            cpu_cores_per_chunk=2,
            ram_gb_per_chunk=4.0
        )
        db_session.add(job)
        db_session.commit()

        assert job.id is not None
        assert job.owner_id == user.id
        assert job.docker_image == "python:3.11-slim"
        assert job.total_chunks == 4
        assert job.status == "pending"

    def test_job_has_default_status_pending(self, db_session):
        """Test that job status defaults to 'pending'."""
        from src.database.models import Job, User

        user = User(username="bob", email="bob@example.com", password_hash="h", api_key="k2")
        db_session.add(user)
        db_session.flush()

        job = Job(
            owner_id=user.id,
            docker_image="ubuntu:22.04",
            total_chunks=2,
            cpu_cores_per_chunk=4,
            ram_gb_per_chunk=8.0
        )
        db_session.add(job)
        db_session.commit()

        assert job.status == "pending"

    def test_job_has_default_priority(self, db_session):
        """Test that priority defaults to 5."""
        from src.database.models import Job, User

        user = User(username="charlie", email="charlie@example.com", password_hash="h", api_key="k3")
        db_session.add(user)
        db_session.flush()

        job = Job(
            owner_id=user.id,
            docker_image="alpine:3.18",
            total_chunks=8,
            cpu_cores_per_chunk=1,
            ram_gb_per_chunk=2.0
        )
        db_session.add(job)
        db_session.commit()

        assert job.priority == 5

    def test_job_has_default_completed_chunks_zero(self, db_session):
        """Test that completed_chunks defaults to 0."""
        from src.database.models import Job, User

        user = User(username="dave", email="dave@example.com", password_hash="h", api_key="k4")
        db_session.add(user)
        db_session.flush()

        job = Job(
            owner_id=user.id,
            docker_image="python:3.11-alpine",
            total_chunks=10,
            cpu_cores_per_chunk=2,
            ram_gb_per_chunk=4.0
        )
        db_session.add(job)
        db_session.commit()

        assert job.completed_chunks == 0


class TestJobChunkModel:
    """Test suite for JobChunk model."""

    def test_job_chunk_can_be_created(self, db_session):
        """Test that a job chunk can be created."""
        from src.database.models import JobChunk, Job, User

        user = User(username="alice", email="alice@example.com", password_hash="h", api_key="k")
        db_session.add(user)
        db_session.flush()

        job = Job(
            owner_id=user.id,
            docker_image="python:3.11-slim",
            total_chunks=4,
            cpu_cores_per_chunk=2,
            ram_gb_per_chunk=4.0
        )
        db_session.add(job)
        db_session.flush()

        chunk = JobChunk(
            job_id=job.id,
            chunk_number=0,
            input_data='{"start": 0, "end": 25000000}'
        )
        db_session.add(chunk)
        db_session.commit()

        assert chunk.id is not None
        assert chunk.job_id == job.id
        assert chunk.chunk_number == 0
        assert chunk.status == "pending"

    def test_job_chunk_has_default_status_pending(self, db_session):
        """Test that chunk status defaults to 'pending'."""
        from src.database.models import JobChunk, Job, User

        user = User(username="bob", email="bob@example.com", password_hash="h", api_key="k2")
        db_session.add(user)
        db_session.flush()

        job = Job(
            owner_id=user.id,
            docker_image="ubuntu:22.04",
            total_chunks=2,
            cpu_cores_per_chunk=4,
            ram_gb_per_chunk=8.0
        )
        db_session.add(job)
        db_session.flush()

        chunk = JobChunk(job_id=job.id, chunk_number=1)
        db_session.add(chunk)
        db_session.commit()

        assert chunk.status == "pending"

    def test_job_chunk_has_default_retry_count_zero(self, db_session):
        """Test that retry_count defaults to 0."""
        from src.database.models import JobChunk, Job, User

        user = User(username="charlie", email="charlie@example.com", password_hash="h", api_key="k3")
        db_session.add(user)
        db_session.flush()

        job = Job(
            owner_id=user.id,
            docker_image="alpine:3.18",
            total_chunks=4,
            cpu_cores_per_chunk=1,
            ram_gb_per_chunk=2.0
        )
        db_session.add(job)
        db_session.flush()

        chunk = JobChunk(job_id=job.id, chunk_number=2)
        db_session.add(chunk)
        db_session.commit()

        assert chunk.retry_count == 0

    def test_job_chunk_unique_constraint(self, db_session):
        """Test that job_id + chunk_number must be unique."""
        from src.database.models import JobChunk, Job, User

        user = User(username="dave", email="dave@example.com", password_hash="h", api_key="k4")
        db_session.add(user)
        db_session.flush()

        job = Job(
            owner_id=user.id,
            docker_image="python:3.11-alpine",
            total_chunks=2,
            cpu_cores_per_chunk=2,
            ram_gb_per_chunk=4.0
        )
        db_session.add(job)
        db_session.flush()

        chunk1 = JobChunk(job_id=job.id, chunk_number=0)
        db_session.add(chunk1)
        db_session.commit()

        # Try to create duplicate
        chunk2 = JobChunk(job_id=job.id, chunk_number=0)
        db_session.add(chunk2)

        with pytest.raises(IntegrityError):
            db_session.commit()


class TestCreditTransactionModel:
    """Test suite for CreditTransaction model."""

    def test_credit_transaction_can_be_created(self, db_session):
        """Test that a credit transaction can be created."""
        from src.database.models import CreditTransaction, User

        sender = User(username="alice", email="alice@example.com", password_hash="h", api_key="k1")
        receiver = User(username="bob", email="bob@example.com", password_hash="h", api_key="k2")
        db_session.add_all([sender, receiver])
        db_session.flush()

        transaction = CreditTransaction(
            from_user_id=sender.id,
            to_user_id=receiver.id,
            amount=100,
            transaction_type="job_payment"
        )
        db_session.add(transaction)
        db_session.commit()

        assert transaction.id is not None
        assert transaction.from_user_id == sender.id
        assert transaction.to_user_id == receiver.id
        assert transaction.amount == 100
        assert transaction.transaction_type == "job_payment"

    def test_credit_transaction_timestamps_auto_populate(self, db_session):
        """Test that created_at is automatically set."""
        from src.database.models import CreditTransaction, User

        user = User(username="charlie", email="charlie@example.com", password_hash="h", api_key="k3")
        db_session.add(user)
        db_session.flush()

        transaction = CreditTransaction(
            to_user_id=user.id,
            amount=100,
            transaction_type="initial_credits"
        )
        db_session.add(transaction)
        db_session.commit()

        assert transaction.created_at is not None
        assert isinstance(transaction.created_at, datetime)

    def test_credit_transaction_allows_null_users(self, db_session):
        """Test that from_user_id and to_user_id can be null (for system transactions)."""
        from src.database.models import CreditTransaction

        # System transaction (no users)
        transaction = CreditTransaction(
            amount=100,
            transaction_type="system_adjustment"
        )
        db_session.add(transaction)
        db_session.commit()

        assert transaction.from_user_id is None
        assert transaction.to_user_id is None
