"""
Tests for marketplace Pydantic models.

Following TDD: These tests are written BEFORE implementation.
Tests for Node, ResourceOffer, Job, and related request/response models.
"""

import pytest
from pydantic import ValidationError
from datetime import datetime


class TestNodeRegisterModel:
    """Test suite for NodeRegister Pydantic model."""

    def test_valid_node_registration_data_passes(self):
        """Test that valid node registration data passes validation."""
        from src.api.marketplace_models import NodeRegister

        node_data = {
            "name": "Alice-Desktop",
            "tailscale_ip": "100.64.0.1",
            "cpu_cores": 8,
            "ram_gb": 16.0,
            "storage_gb": 500.0
        }

        node = NodeRegister(**node_data)

        assert node.name == "Alice-Desktop"
        assert node.tailscale_ip == "100.64.0.1"
        assert node.cpu_cores == 8
        assert node.ram_gb == 16.0
        assert node.storage_gb == 500.0

    def test_node_name_required(self):
        """Test that node name is required."""
        from src.api.marketplace_models import NodeRegister

        node_data = {
            "tailscale_ip": "100.64.0.1",
            "cpu_cores": 8,
            "ram_gb": 16.0,
            "storage_gb": 500.0
        }

        with pytest.raises(ValidationError) as exc_info:
            NodeRegister(**node_data)

        assert "name" in str(exc_info.value)

    def test_node_cpu_cores_must_be_positive(self):
        """Test that CPU cores must be at least 1."""
        from src.api.marketplace_models import NodeRegister

        node_data = {
            "name": "Test-Node",
            "tailscale_ip": "100.64.0.1",
            "cpu_cores": 0,
            "ram_gb": 16.0,
            "storage_gb": 500.0
        }

        with pytest.raises(ValidationError):
            NodeRegister(**node_data)

    def test_node_ram_must_be_positive(self):
        """Test that RAM must be greater than 0."""
        from src.api.marketplace_models import NodeRegister

        node_data = {
            "name": "Test-Node",
            "tailscale_ip": "100.64.0.1",
            "cpu_cores": 4,
            "ram_gb": -1.0,
            "storage_gb": 500.0
        }

        with pytest.raises(ValidationError):
            NodeRegister(**node_data)


class TestNodeResponseModel:
    """Test suite for NodeResponse Pydantic model."""

    def test_node_response_creation(self):
        """Test that NodeResponse can be created from valid data."""
        from src.api.marketplace_models import NodeResponse

        node_data = {
            "id": 1,
            "owner_id": 1,
            "name": "Alice-Desktop",
            "tailscale_ip": "100.64.0.1",
            "cpu_cores": 8,
            "ram_gb": 16.0,
            "storage_gb": 500.0,
            "status": "online",
            "created_at": datetime.now()
        }

        node = NodeResponse(**node_data)

        assert node.id == 1
        assert node.name == "Alice-Desktop"
        assert node.status == "online"

    def test_node_response_from_orm(self):
        """Test that NodeResponse works with ORM mode."""
        from src.api.marketplace_models import NodeResponse
        from src.database.models import Node, User

        # Create mock ORM object
        class MockNode:
            id = 1
            owner_id = 1
            name = "Test-Node"
            tailscale_ip = "100.64.0.1"
            cpu_cores = 4
            ram_gb = 8.0
            storage_gb = 200.0
            status = "offline"
            last_heartbeat = None
            created_at = datetime.now()

        node = NodeResponse.model_validate(MockNode())

        assert node.id == 1
        assert node.name == "Test-Node"


class TestResourceOfferCreateModel:
    """Test suite for ResourceOfferCreate Pydantic model."""

    def test_valid_resource_offer_creation(self):
        """Test that valid resource offer data passes validation."""
        from src.api.marketplace_models import ResourceOfferCreate

        offer_data = {
            "node_id": 1,
            "cpu_cores_available": 4,
            "ram_gb_available": 8.0,
            "storage_gb_available": 100.0,
            "offer_type": "paid"
        }

        offer = ResourceOfferCreate(**offer_data)

        assert offer.node_id == 1
        assert offer.cpu_cores_available == 4
        assert offer.offer_type == "paid"

    def test_offer_type_must_be_valid(self):
        """Test that offer_type must be 'paid' or 'free'."""
        from src.api.marketplace_models import ResourceOfferCreate

        offer_data = {
            "node_id": 1,
            "cpu_cores_available": 4,
            "ram_gb_available": 8.0,
            "storage_gb_available": 100.0,
            "offer_type": "invalid"
        }

        with pytest.raises(ValidationError):
            ResourceOfferCreate(**offer_data)

    def test_approval_policy_defaults_to_manual(self):
        """Test that approval_policy defaults to 'manual'."""
        from src.api.marketplace_models import ResourceOfferCreate

        offer_data = {
            "node_id": 1,
            "cpu_cores_available": 4,
            "ram_gb_available": 8.0,
            "storage_gb_available": 100.0,
            "offer_type": "paid"
        }

        offer = ResourceOfferCreate(**offer_data)

        assert offer.approval_policy == "manual"

    def test_trusted_users_optional(self):
        """Test that trusted_users is optional."""
        from src.api.marketplace_models import ResourceOfferCreate

        offer_data = {
            "node_id": 1,
            "cpu_cores_available": 4,
            "ram_gb_available": 8.0,
            "storage_gb_available": 100.0,
            "offer_type": "free"
        }

        offer = ResourceOfferCreate(**offer_data)

        assert offer.trusted_users is None


class TestResourceOfferResponseModel:
    """Test suite for ResourceOfferResponse Pydantic model."""

    def test_resource_offer_response_creation(self):
        """Test that ResourceOfferResponse can be created."""
        from src.api.marketplace_models import ResourceOfferResponse

        offer_data = {
            "id": 1,
            "node_id": 1,
            "cpu_cores_available": 4,
            "ram_gb_available": 8.0,
            "storage_gb_available": 100.0,
            "offer_type": "paid",
            "approval_policy": "manual",
            "trusted_users": None,
            "active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        offer = ResourceOfferResponse(**offer_data)

        assert offer.id == 1
        assert offer.offer_type == "paid"
        assert offer.active is True


class TestJobSubmitModel:
    """Test suite for JobSubmit Pydantic model."""

    def test_valid_job_submission(self):
        """Test that valid job submission data passes validation."""
        from src.api.marketplace_models import JobSubmit

        job_data = {
            "docker_image": "python:3.11-slim",
            "total_chunks": 4,
            "cpu_cores_per_chunk": 2,
            "ram_gb_per_chunk": 4.0
        }

        job = JobSubmit(**job_data)

        assert job.docker_image == "python:3.11-slim"
        assert job.total_chunks == 4
        assert job.cpu_cores_per_chunk == 2

    def test_docker_image_required(self):
        """Test that docker_image is required."""
        from src.api.marketplace_models import JobSubmit

        job_data = {
            "total_chunks": 4,
            "cpu_cores_per_chunk": 2,
            "ram_gb_per_chunk": 4.0
        }

        with pytest.raises(ValidationError):
            JobSubmit(**job_data)

    def test_total_chunks_must_be_positive(self):
        """Test that total_chunks must be at least 1."""
        from src.api.marketplace_models import JobSubmit

        job_data = {
            "docker_image": "python:3.11-slim",
            "total_chunks": 0,
            "cpu_cores_per_chunk": 2,
            "ram_gb_per_chunk": 4.0
        }

        with pytest.raises(ValidationError):
            JobSubmit(**job_data)

    def test_priority_optional_with_default(self):
        """Test that priority is optional and defaults to 5."""
        from src.api.marketplace_models import JobSubmit

        job_data = {
            "docker_image": "python:3.11-slim",
            "total_chunks": 4,
            "cpu_cores_per_chunk": 2,
            "ram_gb_per_chunk": 4.0
        }

        job = JobSubmit(**job_data)

        assert job.priority == 5

    def test_priority_must_be_in_range(self):
        """Test that priority must be between 1 and 10."""
        from src.api.marketplace_models import JobSubmit

        job_data = {
            "docker_image": "python:3.11-slim",
            "total_chunks": 4,
            "cpu_cores_per_chunk": 2,
            "ram_gb_per_chunk": 4.0,
            "priority": 11
        }

        with pytest.raises(ValidationError):
            JobSubmit(**job_data)


class TestJobResponseModel:
    """Test suite for JobResponse Pydantic model."""

    def test_job_response_creation(self):
        """Test that JobResponse can be created."""
        from src.api.marketplace_models import JobResponse

        job_data = {
            "id": 1,
            "owner_id": 1,
            "docker_image": "python:3.11-slim",
            "total_chunks": 4,
            "completed_chunks": 0,
            "status": "pending",
            "priority": 5,
            "cpu_cores_per_chunk": 2,
            "ram_gb_per_chunk": 4.0,
            "created_at": datetime.now()
        }

        job = JobResponse(**job_data)

        assert job.id == 1
        assert job.status == "pending"
        assert job.total_chunks == 4

    def test_job_response_includes_progress(self):
        """Test that job response shows progress."""
        from src.api.marketplace_models import JobResponse

        job_data = {
            "id": 1,
            "owner_id": 1,
            "docker_image": "python:3.11-slim",
            "total_chunks": 4,
            "completed_chunks": 2,
            "status": "running",
            "priority": 5,
            "cpu_cores_per_chunk": 2,
            "ram_gb_per_chunk": 4.0,
            "created_at": datetime.now()
        }

        job = JobResponse(**job_data)

        assert job.completed_chunks == 2
        assert job.total_chunks == 4


class TestNodeUpdateModel:
    """Test suite for NodeUpdate Pydantic model."""

    def test_node_update_all_fields_optional(self):
        """Test that all fields in NodeUpdate are optional."""
        from src.api.marketplace_models import NodeUpdate

        # Empty update should be valid
        update = NodeUpdate()

        assert update.model_dump(exclude_unset=True) == {}

    def test_node_update_partial_update(self):
        """Test partial update with only some fields."""
        from src.api.marketplace_models import NodeUpdate

        update = NodeUpdate(status="maintenance")

        assert update.status == "maintenance"
        assert update.cpu_cores is None
