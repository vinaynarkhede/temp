"""
Fault tolerance module for handling node failures and chunk reallocation.

Detects orphaned chunks (assigned to offline nodes) and reallocates them.
"""

import logging
from typing import List
from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import JobChunk, Node


logger = logging.getLogger(__name__)


# Maximum retries before marking chunk as failed
MAX_RETRIES = 3


def find_orphaned_chunks(db: Session) -> List[JobChunk]:
    """
    Find chunks assigned to offline nodes.

    Args:
        db: Database session

    Returns:
        List of orphaned job chunks
    """
    # Find chunks in 'running' status assigned to offline nodes
    orphaned = db.query(JobChunk).join(Node, JobChunk.assigned_node_id == Node.id).filter(
        and_(
            JobChunk.status == 'running',
            Node.status == 'offline'
        )
    ).all()

    logger.info(f"Found {len(orphaned)} orphaned chunks")
    return orphaned


def reallocate_orphaned_chunks(db: Session) -> int:
    """
    Reset orphaned chunks to pending status for rescheduling.

    Args:
        db: Database session

    Returns:
        Number of chunks reallocated
    """
    orphaned = find_orphaned_chunks(db)
    reallocated_count = 0

    for chunk in orphaned:
        # Check if chunk has exceeded max retries
        if chunk.retry_count >= MAX_RETRIES:
            # Mark as failed after max retries
            chunk.status = 'failed'
            logger.warning(f"Chunk {chunk.id} failed after {MAX_RETRIES} retries")
        else:
            # Reset to pending for reallocation
            chunk.status = 'pending'
            chunk.assigned_node_id = None
            chunk.retry_count += 1
            reallocated_count += 1
            logger.info(f"Reallocated chunk {chunk.id} (retry #{chunk.retry_count})")

    if reallocated_count > 0 or len(orphaned) > len([c for c in orphaned if c.retry_count >= MAX_RETRIES]):
        db.commit()

    return reallocated_count


def check_job_completion(db: Session) -> int:
    """
    Check for completed jobs and update their status.

    Args:
        db: Database session

    Returns:
        Number of jobs marked as completed
    """
    from src.database.models import Job

    # Find running jobs where all chunks are completed
    running_jobs = db.query(Job).filter(Job.status == 'running').all()
    completed_count = 0

    for job in running_jobs:
        # Get all chunks for this job
        chunks = db.query(JobChunk).filter(JobChunk.job_id == job.id).all()

        if not chunks:
            continue

        # Check if all chunks are completed
        all_completed = all(chunk.status == 'completed' for chunk in chunks)

        if all_completed:
            job.status = 'completed'
            job.completed_chunks = len(chunks)
            completed_count += 1
            logger.info(f"Job {job.id} completed ({len(chunks)} chunks)")

    if completed_count > 0:
        db.commit()

    return completed_count
