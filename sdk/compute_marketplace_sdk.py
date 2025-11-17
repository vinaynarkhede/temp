"""
Python SDK for Compute Marketplace.

Simple client library for interacting with the marketplace API.
"""

import requests
from typing import Optional, Dict, List


class ComputeMarketplaceClient:
    """Client for Compute Marketplace API."""

    def __init__(self, base_url: str, api_key: str):
        """
        Initialize client.

        Args:
            base_url: API base URL (e.g., "http://localhost:8000")
            api_key: User API key
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key})

    def submit_job(
        self,
        docker_image: str,
        total_chunks: int,
        cpu_cores_per_chunk: int,
        ram_gb_per_chunk: float,
        estimated_duration_hours: float = 1.0,
        priority: int = 5
    ) -> Dict:
        """
        Submit a compute job.

        Args:
            docker_image: Docker image to run
            total_chunks: Number of chunks to split job into
            cpu_cores_per_chunk: CPU cores per chunk
            ram_gb_per_chunk: RAM per chunk in GB
            estimated_duration_hours: Estimated duration
            priority: Job priority (1-10)

        Returns:
            Job details
        """
        response = self.session.post(
            f"{self.base_url}/jobs",
            json={
                "docker_image": docker_image,
                "total_chunks": total_chunks,
                "cpu_cores_per_chunk": cpu_cores_per_chunk,
                "ram_gb_per_chunk": ram_gb_per_chunk,
                "estimated_duration_hours": estimated_duration_hours,
                "priority": priority
            }
        )
        response.raise_for_status()
        return response.json()

    def get_job(self, job_id: int) -> Dict:
        """Get job details."""
        response = self.session.get(f"{self.base_url}/jobs/{job_id}")
        response.raise_for_status()
        return response.json()

    def list_jobs(self) -> List[Dict]:
        """List all jobs."""
        response = self.session.get(f"{self.base_url}/jobs")
        response.raise_for_status()
        return response.json()

    def cancel_job(self, job_id: int) -> Dict:
        """Cancel a running job."""
        response = self.session.post(f"{self.base_url}/jobs/{job_id}/cancel")
        response.raise_for_status()
        return response.json()

    def get_job_chunks(self, job_id: int) -> List[Dict]:
        """Get all chunks for a job."""
        response = self.session.get(f"{self.base_url}/jobs/{job_id}/chunks")
        response.raise_for_status()
        return response.json()

    def register_node(
        self,
        name: str,
        tailscale_ip: str,
        cpu_cores: int,
        ram_gb: float,
        storage_gb: float
    ) -> Dict:
        """Register a compute node."""
        response = self.session.post(
            f"{self.base_url}/nodes",
            json={
                "name": name,
                "tailscale_ip": tailscale_ip,
                "cpu_cores": cpu_cores,
                "ram_gb": ram_gb,
                "storage_gb": storage_gb
            }
        )
        response.raise_for_status()
        return response.json()

    def list_offers(self) -> List[Dict]:
        """Browse available resource offers."""
        response = self.session.get(f"{self.base_url}/offers")
        response.raise_for_status()
        return response.json()

    def get_balance(self) -> int:
        """Get current credit balance."""
        response = self.session.get(f"{self.base_url}/auth/me")
        response.raise_for_status()
        return response.json()["credit_balance"]


# Example usage
if __name__ == "__main__":
    client = ComputeMarketplaceClient(
        base_url="http://localhost:8000",
        api_key="your-api-key-here"
    )

    # Submit job
    job = client.submit_job(
        docker_image="python:3.11-slim",
        total_chunks=4,
        cpu_cores_per_chunk=2,
        ram_gb_per_chunk=4.0
    )
    print(f"Submitted job {job['id']}")

    # Check status
    status = client.get_job(job["id"])
    print(f"Job status: {status['status']}")
