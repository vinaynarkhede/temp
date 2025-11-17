"""
Tests for coordinator job scheduler.

Following TDD: These tests verify job scheduling logic.
"""

import pytest
from datetime import datetime


class TestFindMatchingOffers:
    """Test suite for finding matching resource offers."""

    def test_find_matching_offers_exact_match(self, db_session):
        """Test finding offers that exactly match requirements."""
        from src.database.models import User, Node, ResourceOffer
        from src.coordinator.scheduler import find_matching_offers

        # Create user and node
        user = User(username="alice", email="alice@example.com", password_hash="h", api_key="key123")
        db_session.add(user)
        db_session.flush()

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
        db_session.flush()

        # Create matching offer
        offer = ResourceOffer(
            node_id=node.id,
            cpu_cores_available=4,
            ram_gb_available=8.0,
            storage_gb_available=100.0,
            offer_type="paid",
            active=True
        )
        db_session.add(offer)
        db_session.commit()

        # Find offers for job needing 4 cores, 8GB RAM
        offers = find_matching_offers(cpu_cores_needed=4, ram_gb_needed=8.0, db=db_session)

        assert len(offers) == 1
        assert offers[0].id == offer.id

    def test_find_matching_offers_requires_sufficient_resources(self, db_session):
        """Test that offers must have sufficient resources."""
        from src.database.models import User, Node, ResourceOffer
        from src.coordinator.scheduler import find_matching_offers

        user = User(username="bob", email="bob@example.com", password_hash="h", api_key="key456")
        db_session.add(user)
        db_session.flush()

        node = Node(
            owner_id=user.id,
            name="Bob-Laptop",
            tailscale_ip="100.64.0.2",
            cpu_cores=4,
            ram_gb=8.0,
            storage_gb=250.0,
            status="online"
        )
        db_session.add(node)
        db_session.flush()

        # Offer has 2 cores, 4GB - insufficient for job needing 4 cores, 8GB
        offer = ResourceOffer(
            node_id=node.id,
            cpu_cores_available=2,
            ram_gb_available=4.0,
            storage_gb_available=50.0,
            offer_type="paid",
            active=True
        )
        db_session.add(offer)
        db_session.commit()

        # Should not match - insufficient resources
        offers = find_matching_offers(cpu_cores_needed=4, ram_gb_needed=8.0, db=db_session)

        assert len(offers) == 0

    def test_find_matching_offers_only_active_offers(self, db_session):
        """Test that only active offers are returned."""
        from src.database.models import User, Node, ResourceOffer
        from src.coordinator.scheduler import find_matching_offers

        user = User(username="charlie", email="charlie@example.com", password_hash="h", api_key="key789")
        db_session.add(user)
        db_session.flush()

        node = Node(
            owner_id=user.id,
            name="Charlie-PC",
            tailscale_ip="100.64.0.3",
            cpu_cores=8,
            ram_gb=16.0,
            storage_gb=500.0,
            status="online"
        )
        db_session.add(node)
        db_session.flush()

        # Inactive offer
        offer = ResourceOffer(
            node_id=node.id,
            cpu_cores_available=4,
            ram_gb_available=8.0,
            storage_gb_available=100.0,
            offer_type="paid",
            active=False  # Not active
        )
        db_session.add(offer)
        db_session.commit()

        offers = find_matching_offers(cpu_cores_needed=4, ram_gb_needed=8.0, db=db_session)

        assert len(offers) == 0

    def test_find_matching_offers_only_online_nodes(self, db_session):
        """Test that only offers from online nodes are returned."""
        from src.database.models import User, Node, ResourceOffer
        from src.coordinator.scheduler import find_matching_offers

        user = User(username="dave", email="dave@example.com", password_hash="h", api_key="key000")
        db_session.add(user)
        db_session.flush()

        node = Node(
            owner_id=user.id,
            name="Dave-Server",
            tailscale_ip="100.64.0.4",
            cpu_cores=16,
            ram_gb=32.0,
            storage_gb=1000.0,
            status="offline"  # Node is offline
        )
        db_session.add(node)
        db_session.flush()

        offer = ResourceOffer(
            node_id=node.id,
            cpu_cores_available=8,
            ram_gb_available=16.0,
            storage_gb_available=200.0,
            offer_type="paid",
            active=True
        )
        db_session.add(offer)
        db_session.commit()

        offers = find_matching_offers(cpu_cores_needed=4, ram_gb_needed=8.0, db=db_session)

        assert len(offers) == 0


class TestSchedulePendingJobs:
    """Test suite for scheduling pending jobs."""

    def test_schedule_pending_jobs_assigns_chunks(self, db_session):
        """Test that pending chunks are assigned to available nodes."""
        from src.database.models import User, Node, ResourceOffer, Job, JobChunk
        from src.coordinator.scheduler import schedule_pending_jobs

        # Create user
        user = User(username="alice", email="alice@example.com", password_hash="h", api_key="key123")
        db_session.add(user)
        db_session.flush()

        # Create online node with offer
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
        db_session.flush()

        offer = ResourceOffer(
            node_id=node.id,
            cpu_cores_available=4,
            ram_gb_available=8.0,
            storage_gb_available=100.0,
            offer_type="paid",
            active=True
        )
        db_session.add(offer)
        db_session.flush()

        # Create job with pending chunks
        job = Job(
            owner_id=user.id,
            docker_image="python:3.11-slim",
            total_chunks=2,
            completed_chunks=0,
            status="pending",
            priority=5,
            cpu_cores_per_chunk=4,
            ram_gb_per_chunk=8.0,
            estimated_duration_hours=1.0
        )
        db_session.add(job)
        db_session.flush()

        chunk1 = JobChunk(job_id=job.id, chunk_number=0, status="pending", retry_count=0)
        chunk2 = JobChunk(job_id=job.id, chunk_number=1, status="pending", retry_count=0)
        db_session.add_all([chunk1, chunk2])
        db_session.commit()

        # Schedule the pending chunks
        scheduled_count = schedule_pending_jobs(db=db_session)

        # Should schedule both chunks
        assert scheduled_count == 2

        # Verify chunks are assigned and status updated
        db_session.refresh(chunk1)
        db_session.refresh(chunk2)

        assert chunk1.assigned_node_id == node.id
        assert chunk1.status == "running"
        assert chunk2.assigned_node_id == node.id
        assert chunk2.status == "running"

    def test_schedule_pending_jobs_skips_insufficient_resources(self, db_session):
        """Test that chunks requiring more resources than available are not scheduled."""
        from src.database.models import User, Node, ResourceOffer, Job, JobChunk
        from src.coordinator.scheduler import schedule_pending_jobs

        user = User(username="bob", email="bob@example.com", password_hash="h", api_key="key456")
        db_session.add(user)
        db_session.flush()

        # Node with limited resources
        node = Node(
            owner_id=user.id,
            name="Bob-Laptop",
            tailscale_ip="100.64.0.2",
            cpu_cores=2,
            ram_gb=4.0,
            storage_gb=100.0,
            status="online"
        )
        db_session.add(node)
        db_session.flush()

        offer = ResourceOffer(
            node_id=node.id,
            cpu_cores_available=2,
            ram_gb_available=4.0,
            storage_gb_available=50.0,
            offer_type="free",
            active=True
        )
        db_session.add(offer)
        db_session.flush()

        # Job requiring more resources than available
        job = Job(
            owner_id=user.id,
            docker_image="python:3.11-slim",
            total_chunks=1,
            completed_chunks=0,
            status="pending",
            priority=5,
            cpu_cores_per_chunk=8,  # More than available (2)
            ram_gb_per_chunk=16.0,  # More than available (4.0)
            estimated_duration_hours=1.0
        )
        db_session.add(job)
        db_session.flush()

        chunk = JobChunk(job_id=job.id, chunk_number=0, status="pending", retry_count=0)
        db_session.add(chunk)
        db_session.commit()

        # Try to schedule
        scheduled_count = schedule_pending_jobs(db=db_session)

        # Should not schedule due to insufficient resources
        assert scheduled_count == 0

        db_session.refresh(chunk)
        assert chunk.assigned_node_id is None
        assert chunk.status == "pending"

    def test_schedule_pending_jobs_returns_zero_when_no_work(self, db_session):
        """Test that scheduler returns 0 when there are no pending chunks."""
        from src.coordinator.scheduler import schedule_pending_jobs

        # No jobs in database
        scheduled_count = schedule_pending_jobs(db=db_session)

        assert scheduled_count == 0

    def test_schedule_pending_jobs_updates_job_status(self, db_session):
        """Test that job status is updated when scheduling starts."""
        from src.database.models import User, Node, ResourceOffer, Job, JobChunk
        from src.coordinator.scheduler import schedule_pending_jobs

        user = User(username="charlie", email="charlie@example.com", password_hash="h", api_key="key789")
        db_session.add(user)
        db_session.flush()

        node = Node(
            owner_id=user.id,
            name="Charlie-PC",
            tailscale_ip="100.64.0.3",
            cpu_cores=8,
            ram_gb=16.0,
            storage_gb=500.0,
            status="online"
        )
        db_session.add(node)
        db_session.flush()

        offer = ResourceOffer(
            node_id=node.id,
            cpu_cores_available=4,
            ram_gb_available=8.0,
            storage_gb_available=100.0,
            offer_type="paid",
            active=True
        )
        db_session.add(offer)
        db_session.flush()

        # Job with pending status
        job = Job(
            owner_id=user.id,
            docker_image="python:3.11-slim",
            total_chunks=1,
            completed_chunks=0,
            status="pending",
            priority=5,
            cpu_cores_per_chunk=4,
            ram_gb_per_chunk=8.0,
            estimated_duration_hours=1.0
        )
        db_session.add(job)
        db_session.flush()

        chunk = JobChunk(job_id=job.id, chunk_number=0, status="pending", retry_count=0)
        db_session.add(chunk)
        db_session.commit()

        schedule_pending_jobs(db=db_session)

        db_session.refresh(job)
        # Job status should be updated to running when chunks are scheduled
        assert job.status == "running"
