"""
Job submission and management API endpoints.

Handles job submission, status tracking, and chunk management.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.models import Job, JobChunk, User
from src.api.marketplace_models import JobSubmit, JobResponse, JobChunkResponse
from src.api.auth import get_current_user


router = APIRouter()


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def submit_job(
    job_data: JobSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a new compute job.

    Creates a job and its associated chunks for fault-tolerant execution.

    Args:
        job_data: Job submission data
        current_user: Authenticated user
        db: Database session

    Returns:
        Created job information

    Raises:
        HTTPException: If validation fails
    """
    # Create job
    job = Job(
        owner_id=current_user.id,
        docker_image=job_data.docker_image,
        total_chunks=job_data.total_chunks,
        completed_chunks=0,
        status="pending",
        priority=job_data.priority,
        cpu_cores_per_chunk=job_data.cpu_cores_per_chunk,
        ram_gb_per_chunk=job_data.ram_gb_per_chunk,
        estimated_duration_hours=job_data.estimated_duration_hours
    )

    db.add(job)
    db.flush()  # Get job ID

    # Create job chunks
    chunks = [
        JobChunk(
            job_id=job.id,
            chunk_number=i,
            status="pending",
            retry_count=0
        )
        for i in range(job_data.total_chunks)
    ]
    db.add_all(chunks)
    db.commit()
    db.refresh(job)

    return JobResponse.model_validate(job)


@router.get("", response_model=List[JobResponse])
async def list_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all jobs owned by the current user.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        List of user's jobs
    """
    jobs = db.query(Job).filter(Job.owner_id == current_user.id).all()

    return [JobResponse.model_validate(job) for job in jobs]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific job.

    Args:
        job_id: Job ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Job information

    Raises:
        HTTPException: If job not found or user not authorized
    """
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Check ownership
    if job.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this job"
        )

    return JobResponse.model_validate(job)


@router.get("/{job_id}/chunks", response_model=List[JobChunkResponse])
async def get_job_chunks(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all chunks for a specific job.

    Args:
        job_id: Job ID
        current_user: Authenticated user
        db: Database session

    Returns:
        List of job chunks

    Raises:
        HTTPException: If job not found or user not authorized
    """
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Check ownership
    if job.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this job's chunks"
        )

    # Get all chunks for this job
    chunks = db.query(JobChunk).filter(JobChunk.job_id == job_id).order_by(JobChunk.chunk_number).all()

    return [JobChunkResponse.model_validate(chunk) for chunk in chunks]


@router.post("/{job_id}/cancel", response_model=JobResponse)
async def cancel_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a pending or running job.

    Args:
        job_id: Job ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated job information

    Raises:
        HTTPException: If job not found or user not authorized
    """
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Check ownership
    if job.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this job"
        )

    # Update job status to failed (cancelled)
    job.status = "failed"
    db.commit()
    db.refresh(job)

    return JobResponse.model_validate(job)
