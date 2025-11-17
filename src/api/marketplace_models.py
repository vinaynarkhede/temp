"""
Pydantic models for marketplace API requests and responses.

These models handle validation for nodes, resource offers, and jobs.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict


class NodeRegister(BaseModel):
    """
    Request model for registering a new compute node.

    Attributes:
        name: Human-readable node name
        tailscale_ip: Tailscale VPN IP address
        cpu_cores: Number of CPU cores available
        ram_gb: RAM available in gigabytes
        storage_gb: Storage available in gigabytes
    """

    name: str = Field(..., min_length=1, max_length=100, description="Node name")
    tailscale_ip: str = Field(..., description="Tailscale VPN IP address")
    cpu_cores: int = Field(..., ge=1, description="Number of CPU cores")
    ram_gb: float = Field(..., gt=0, description="RAM in GB")
    storage_gb: float = Field(..., gt=0, description="Storage in GB")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Alice-Desktop",
                "tailscale_ip": "100.64.0.1",
                "cpu_cores": 8,
                "ram_gb": 16.0,
                "storage_gb": 500.0
            }
        }
    )


class NodeUpdate(BaseModel):
    """
    Request model for updating node information.

    All fields are optional to allow partial updates.

    Attributes:
        cpu_cores: Updated CPU core count
        ram_gb: Updated RAM amount
        storage_gb: Updated storage amount
        status: Updated node status
    """

    cpu_cores: Optional[int] = Field(None, ge=1)
    ram_gb: Optional[float] = Field(None, gt=0)
    storage_gb: Optional[float] = Field(None, gt=0)
    status: Optional[str] = Field(None, pattern="^(online|offline|maintenance)$")


class NodeResponse(BaseModel):
    """
    Response model for node information.

    Attributes:
        id: Unique node ID
        owner_id: ID of user who owns this node
        name: Node name
        tailscale_ip: Tailscale VPN IP
        cpu_cores: CPU cores available
        ram_gb: RAM in GB
        storage_gb: Storage in GB
        status: Node status
        last_heartbeat: Last heartbeat timestamp
        created_at: Node registration timestamp
    """

    id: int
    owner_id: int
    name: str
    tailscale_ip: str
    cpu_cores: int
    ram_gb: float
    storage_gb: float
    status: str
    last_heartbeat: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResourceOfferCreate(BaseModel):
    """
    Request model for creating a resource offer.

    Attributes:
        node_id: ID of node offering resources
        cpu_cores_available: CPU cores to offer
        ram_gb_available: RAM to offer in GB
        storage_gb_available: Storage to offer in GB
        offer_type: 'paid' or 'free'
        approval_policy: 'auto_all', 'auto_friends', or 'manual'
        trusted_users: List of user IDs for auto-approval (optional)
    """

    node_id: int = Field(..., description="Node ID")
    cpu_cores_available: int = Field(..., ge=1, description="CPU cores offered")
    ram_gb_available: float = Field(..., gt=0, description="RAM offered in GB")
    storage_gb_available: float = Field(..., gt=0, description="Storage offered in GB")
    offer_type: str = Field(..., pattern="^(paid|free)$", description="Offer type")
    approval_policy: str = Field(
        default="manual",
        pattern="^(auto_all|auto_friends|manual)$",
        description="Approval policy"
    )
    trusted_users: Optional[List[int]] = Field(None, description="Trusted user IDs")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "node_id": 1,
                "cpu_cores_available": 4,
                "ram_gb_available": 8.0,
                "storage_gb_available": 100.0,
                "offer_type": "paid",
                "approval_policy": "manual"
            }
        }
    )


class ResourceOfferUpdate(BaseModel):
    """
    Request model for updating a resource offer.

    All fields are optional to allow partial updates.

    Attributes:
        cpu_cores_available: Updated CPU cores
        ram_gb_available: Updated RAM
        storage_gb_available: Updated storage
        approval_policy: Updated approval policy
        trusted_users: Updated trusted users list
        active: Whether offer is active
    """

    cpu_cores_available: Optional[int] = Field(None, ge=1)
    ram_gb_available: Optional[float] = Field(None, gt=0)
    storage_gb_available: Optional[float] = Field(None, gt=0)
    approval_policy: Optional[str] = Field(None, pattern="^(auto_all|auto_friends|manual)$")
    trusted_users: Optional[List[int]] = None
    active: Optional[bool] = None


class ResourceOfferResponse(BaseModel):
    """
    Response model for resource offer information.

    Attributes:
        id: Unique offer ID
        node_id: Node ID
        cpu_cores_available: CPU cores offered
        ram_gb_available: RAM offered in GB
        storage_gb_available: Storage offered in GB
        offer_type: Offer type (paid/free)
        approval_policy: Approval policy
        trusted_users: Trusted user IDs
        active: Whether offer is active
        created_at: Offer creation timestamp
        updated_at: Last update timestamp
    """

    id: int
    node_id: int
    cpu_cores_available: int
    ram_gb_available: float
    storage_gb_available: float
    offer_type: str
    approval_policy: str
    trusted_users: Optional[List[int]] = None
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobSubmit(BaseModel):
    """
    Request model for submitting a compute job.

    Attributes:
        docker_image: Docker image to run
        total_chunks: Number of chunks to split job into
        cpu_cores_per_chunk: CPU cores needed per chunk
        ram_gb_per_chunk: RAM needed per chunk in GB
        priority: Job priority (1=highest, 10=lowest)
        estimated_duration_hours: Estimated runtime in hours (optional)
    """

    docker_image: str = Field(..., min_length=1, max_length=255, description="Docker image")
    total_chunks: int = Field(..., ge=1, description="Number of chunks")
    cpu_cores_per_chunk: int = Field(..., ge=1, description="CPU cores per chunk")
    ram_gb_per_chunk: float = Field(..., gt=0, description="RAM per chunk in GB")
    priority: int = Field(default=5, ge=1, le=10, description="Job priority (1-10)")
    estimated_duration_hours: Optional[float] = Field(None, gt=0, description="Estimated duration")

    @field_validator('docker_image')
    @classmethod
    def validate_docker_image(cls, v: str) -> str:
        """
        Validate that docker image is from approved base images.

        Args:
            v: Docker image string

        Returns:
            Validated docker image string

        Raises:
            ValueError: If image is not from approved base images
        """
        approved_bases = [
            'python:3.11-slim',
            'python:3.11-alpine',
            'ubuntu:22.04',
            'ubuntu:24.04',
            'alpine:3.18',
            'alpine:3.19',
        ]

        if not any(v.startswith(base) for base in approved_bases):
            raise ValueError(
                f"Docker image must be from approved base images: {', '.join(approved_bases)}"
            )

        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "docker_image": "python:3.11-slim",
                "total_chunks": 4,
                "cpu_cores_per_chunk": 2,
                "ram_gb_per_chunk": 4.0,
                "priority": 5
            }
        }
    )


class JobResponse(BaseModel):
    """
    Response model for job information.

    Attributes:
        id: Unique job ID
        owner_id: ID of user who submitted the job
        docker_image: Docker image
        total_chunks: Total number of chunks
        completed_chunks: Number of completed chunks
        status: Job status
        priority: Job priority
        cpu_cores_per_chunk: CPU cores per chunk
        ram_gb_per_chunk: RAM per chunk in GB
        estimated_duration_hours: Estimated duration
        created_at: Job submission timestamp
        completed_at: Job completion timestamp
    """

    id: int
    owner_id: int
    docker_image: str
    total_chunks: int
    completed_chunks: int
    status: str
    priority: int
    cpu_cores_per_chunk: int
    ram_gb_per_chunk: float
    estimated_duration_hours: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class JobChunkResponse(BaseModel):
    """
    Response model for job chunk information.

    Attributes:
        id: Unique chunk ID
        job_id: Job ID
        chunk_number: Chunk number
        assigned_node_id: Assigned node ID
        status: Chunk status
        started_at: Start timestamp
        completed_at: Completion timestamp
        retry_count: Number of retries
    """

    id: int
    job_id: int
    chunk_number: int
    assigned_node_id: Optional[int] = None
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int

    model_config = ConfigDict(from_attributes=True)
