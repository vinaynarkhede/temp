"""
Tests for job submission and management API endpoints.

Following TDD: These tests are written BEFORE implementation.
"""

import pytest
from datetime import datetime


class TestJobSubmission:
    """Test suite for POST /jobs endpoint."""

    def test_submit_job_successfully(self, client, db_session):
        """Test that authenticated user can submit a job."""
        from src.database.models import User

        user = User(
            username="alice",
            email="alice@example.com",
            password_hash="h",
            api_key="key123",
            credit_balance=100
        )
        db_session.add(user)
        db_session.commit()

        job_data = {
            "docker_image": "python:3.11-slim",
            "total_chunks": 4,
            "cpu_cores_per_chunk": 2,
            "ram_gb_per_chunk": 4.0,
            "priority": 5
        }

        response = client.post("/jobs", json=job_data, headers={"X-API-Key": "key123"})

        assert response.status_code == 201
        data = response.json()
        assert data["docker_image"] == "python:3.11-slim"
        assert data["total_chunks"] == 4
        assert data["completed_chunks"] == 0
        assert data["status"] == "pending"
        assert data["owner_id"] == user.id
        assert "id" in data

    def test_submit_job_requires_authentication(self, client):
        """Test that job submission requires API key."""
        job_data = {
            "docker_image": "python:3.11-slim",
            "total_chunks": 4,
            "cpu_cores_per_chunk": 2,
            "ram_gb_per_chunk": 4.0
        }

        response = client.post("/jobs", json=job_data)

        assert response.status_code == 401

    def test_submit_job_validates_docker_image(self, client, db_session):
        """Test that Docker image must be from approved list."""
        from src.database.models import User

        user = User(username="bob", email="bob@example.com", password_hash="h", api_key="key123")
        db_session.add(user)
        db_session.commit()

        job_data = {
            "docker_image": "malicious:latest",
            "total_chunks": 4,
            "cpu_cores_per_chunk": 2,
            "ram_gb_per_chunk": 4.0
        }

        response = client.post("/jobs", json=job_data, headers={"X-API-Key": "key123"})

        assert response.status_code == 422

    def test_submit_job_creates_chunks(self, client, db_session):
        """Test that submitting job creates job chunks."""
        from src.database.models import User, JobChunk

        user = User(username="charlie", email="charlie@example.com", password_hash="h", api_key="key123")
        db_session.add(user)
        db_session.commit()

        job_data = {
            "docker_image": "python:3.11-slim",
            "total_chunks": 3,
            "cpu_cores_per_chunk": 2,
            "ram_gb_per_chunk": 4.0
        }

        response = client.post("/jobs", json=job_data, headers={"X-API-Key": "key123"})

        assert response.status_code == 201
        job_id = response.json()["id"]

        # Verify chunks were created
        chunks = db_session.query(JobChunk).filter(JobChunk.job_id == job_id).all()
        assert len(chunks) == 3
        assert all(chunk.status == "pending" for chunk in chunks)
        assert [chunk.chunk_number for chunk in chunks] == [0, 1, 2]


class TestListJobs:
    """Test suite for GET /jobs endpoint."""

    def test_list_user_jobs(self, client, db_session):
        """Test that user can list their own jobs."""
        from src.database.models import User, Job

        user = User(username="alice", email="alice@example.com", password_hash="h", api_key="key123")
        db_session.add(user)
        db_session.flush()

        job1 = Job(
            owner_id=user.id,
            docker_image="python:3.11-slim",
            total_chunks=4,
            cpu_cores_per_chunk=2,
            ram_gb_per_chunk=4.0
        )
        job2 = Job(
            owner_id=user.id,
            docker_image="ubuntu:22.04",
            total_chunks=2,
            cpu_cores_per_chunk=4,
            ram_gb_per_chunk=8.0
        )
        db_session.add_all([job1, job2])
        db_session.commit()

        response = client.get("/jobs", headers={"X-API-Key": "key123"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_jobs_requires_authentication(self, client):
        """Test that listing jobs requires API key."""
        response = client.get("/jobs")

        assert response.status_code == 401

    def test_list_jobs_only_shows_user_jobs(self, client, db_session):
        """Test that users only see their own jobs."""
        from src.database.models import User, Job

        user1 = User(username="alice", email="alice@example.com", password_hash="h", api_key="key1")
        user2 = User(username="bob", email="bob@example.com", password_hash="h", api_key="key2")
        db_session.add_all([user1, user2])
        db_session.flush()

        job1 = Job(
            owner_id=user1.id,
            docker_image="python:3.11-slim",
            total_chunks=4,
            cpu_cores_per_chunk=2,
            ram_gb_per_chunk=4.0
        )
        job2 = Job(
            owner_id=user2.id,
            docker_image="ubuntu:22.04",
            total_chunks=2,
            cpu_cores_per_chunk=4,
            ram_gb_per_chunk=8.0
        )
        db_session.add_all([job1, job2])
        db_session.commit()

        response = client.get("/jobs", headers={"X-API-Key": "key1"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["docker_image"] == "python:3.11-slim"


class TestGetJobById:
    """Test suite for GET /jobs/{job_id} endpoint."""

    def test_get_job_by_id(self, client, db_session):
        """Test that user can get their job by ID."""
        from src.database.models import User, Job

        user = User(username="alice", email="alice@example.com", password_hash="h", api_key="key123")
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

        response = client.get(f"/jobs/{job.id}", headers={"X-API-Key": "key123"})

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job.id
        assert data["docker_image"] == "python:3.11-slim"

    def test_get_job_requires_authentication(self, client):
        """Test that getting job requires API key."""
        response = client.get("/jobs/1")

        assert response.status_code == 401

    def test_get_job_not_found(self, client, db_session):
        """Test that non-existent job returns 404."""
        from src.database.models import User

        user = User(username="alice", email="alice@example.com", password_hash="h", api_key="key123")
        db_session.add(user)
        db_session.commit()

        response = client.get("/jobs/9999", headers={"X-API-Key": "key123"})

        assert response.status_code == 404

    def test_get_job_forbidden_for_non_owner(self, client, db_session):
        """Test that users cannot access other users' jobs."""
        from src.database.models import User, Job

        user1 = User(username="alice", email="alice@example.com", password_hash="h", api_key="key1")
        user2 = User(username="bob", email="bob@example.com", password_hash="h", api_key="key2")
        db_session.add_all([user1, user2])
        db_session.flush()

        job = Job(
            owner_id=user1.id,
            docker_image="python:3.11-slim",
            total_chunks=4,
            cpu_cores_per_chunk=2,
            ram_gb_per_chunk=4.0
        )
        db_session.add(job)
        db_session.commit()

        # Bob tries to access Alice's job
        response = client.get(f"/jobs/{job.id}", headers={"X-API-Key": "key2"})

        assert response.status_code == 403


class TestGetJobChunks:
    """Test suite for GET /jobs/{job_id}/chunks endpoint."""

    def test_get_job_chunks(self, client, db_session):
        """Test that user can get chunks for their job."""
        from src.database.models import User, Job, JobChunk

        user = User(username="alice", email="alice@example.com", password_hash="h", api_key="key123")
        db_session.add(user)
        db_session.flush()

        job = Job(
            owner_id=user.id,
            docker_image="python:3.11-slim",
            total_chunks=3,
            cpu_cores_per_chunk=2,
            ram_gb_per_chunk=4.0
        )
        db_session.add(job)
        db_session.flush()

        chunks = [
            JobChunk(job_id=job.id, chunk_number=0, status="completed"),
            JobChunk(job_id=job.id, chunk_number=1, status="running"),
            JobChunk(job_id=job.id, chunk_number=2, status="pending")
        ]
        db_session.add_all(chunks)
        db_session.commit()

        response = client.get(f"/jobs/{job.id}/chunks", headers={"X-API-Key": "key123"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["chunk_number"] == 0
        assert data[0]["status"] == "completed"

    def test_get_job_chunks_requires_ownership(self, client, db_session):
        """Test that users can only get chunks for their own jobs."""
        from src.database.models import User, Job

        user1 = User(username="alice", email="alice@example.com", password_hash="h", api_key="key1")
        user2 = User(username="bob", email="bob@example.com", password_hash="h", api_key="key2")
        db_session.add_all([user1, user2])
        db_session.flush()

        job = Job(
            owner_id=user1.id,
            docker_image="python:3.11-slim",
            total_chunks=3,
            cpu_cores_per_chunk=2,
            ram_gb_per_chunk=4.0
        )
        db_session.add(job)
        db_session.commit()

        # Bob tries to access Alice's job chunks
        response = client.get(f"/jobs/{job.id}/chunks", headers={"X-API-Key": "key2"})

        assert response.status_code == 403


class TestCancelJob:
    """Test suite for POST /jobs/{job_id}/cancel endpoint."""

    def test_cancel_job_successfully(self, client, db_session):
        """Test that user can cancel their pending job."""
        from src.database.models import User, Job

        user = User(username="alice", email="alice@example.com", password_hash="h", api_key="key123")
        db_session.add(user)
        db_session.flush()

        job = Job(
            owner_id=user.id,
            docker_image="python:3.11-slim",
            total_chunks=4,
            cpu_cores_per_chunk=2,
            ram_gb_per_chunk=4.0,
            status="pending"
        )
        db_session.add(job)
        db_session.commit()

        response = client.post(f"/jobs/{job.id}/cancel", headers={"X-API-Key": "key123"})

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"

    def test_cancel_job_requires_ownership(self, client, db_session):
        """Test that users can only cancel their own jobs."""
        from src.database.models import User, Job

        user1 = User(username="alice", email="alice@example.com", password_hash="h", api_key="key1")
        user2 = User(username="bob", email="bob@example.com", password_hash="h", api_key="key2")
        db_session.add_all([user1, user2])
        db_session.flush()

        job = Job(
            owner_id=user1.id,
            docker_image="python:3.11-slim",
            total_chunks=4,
            cpu_cores_per_chunk=2,
            ram_gb_per_chunk=4.0,
            status="pending"
        )
        db_session.add(job)
        db_session.commit()

        # Bob tries to cancel Alice's job
        response = client.post(f"/jobs/{job.id}/cancel", headers={"X-API-Key": "key2"})

        assert response.status_code == 403
