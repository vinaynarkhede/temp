"""
Credit calculation utilities for the marketplace.

Calculates credit costs for resource usage based on CPU, RAM, and duration.
"""

from typing import Dict


# Credit weights for different resources
CREDIT_WEIGHTS: Dict[str, int] = {
    'cpu_core_per_hour': 10,
    'ram_gb_per_hour': 2,
    'storage_gb_per_hour': 1
}


def calculate_job_cost(
    cpu_cores: int,
    ram_gb: float,
    estimated_duration_hours: float = 1.0
) -> int:
    """
    Calculate total credit cost for a job.

    Args:
        cpu_cores: Number of CPU cores
        ram_gb: Amount of RAM in gigabytes
        estimated_duration_hours: Estimated job duration in hours

    Returns:
        Total credits required

    Raises:
        ValueError: If any parameter is negative

    Example:
        >>> calculate_job_cost(cpu_cores=4, ram_gb=8, estimated_duration_hours=2.0)
        96
    """
    if cpu_cores < 0 or ram_gb < 0 or estimated_duration_hours < 0:
        raise ValueError("All parameters must be non-negative")

    hourly_cost = (
        cpu_cores * CREDIT_WEIGHTS['cpu_core_per_hour'] +
        ram_gb * CREDIT_WEIGHTS['ram_gb_per_hour']
    )

    return int(hourly_cost * estimated_duration_hours)


def calculate_chunk_cost(
    cpu_cores_per_chunk: int,
    ram_gb_per_chunk: float,
    total_chunks: int,
    estimated_duration_hours: float = 1.0
) -> int:
    """
    Calculate total cost for a chunked job.

    Args:
        cpu_cores_per_chunk: CPU cores per chunk
        ram_gb_per_chunk: RAM per chunk in GB
        total_chunks: Total number of chunks
        estimated_duration_hours: Estimated duration per chunk

    Returns:
        Total credits required for all chunks

    Example:
        >>> calculate_chunk_cost(2, 4.0, 4, 1.0)
        72
    """
    single_chunk_cost = calculate_job_cost(
        cpu_cores_per_chunk,
        ram_gb_per_chunk,
        estimated_duration_hours
    )

    return single_chunk_cost * total_chunks
