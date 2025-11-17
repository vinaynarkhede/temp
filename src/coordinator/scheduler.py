"""
Job scheduler for the distributed compute marketplace.

Matches pending jobs with available nodes and assigns chunks for execution.
"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.database.models import Job, JobChunk, Node, ResourceOffer


logger = logging.getLogger(__name__)


def find_matching_offers(
    cpu_cores_needed: int,
    ram_gb_needed: float,
    db: Session
) -> List[ResourceOffer]:
    """
    Find resource offers that match job requirements.

    Args:
        cpu_cores_needed: CPU cores required
        ram_gb_needed: RAM required in GB
        db: Database session

    Returns:
        List of matching resource offers
    """
    offers = db.query(ResourceOffer).join(Node).filter(
        and_(
            ResourceOffer.active == True,
            ResourceOffer.cpu_cores_available >= cpu_cores_needed,
            ResourceOffer.ram_gb_available >= ram_gb_needed,
            Node.status == 'online'
        )
    ).all()

    return offers


def assign_chunk_to_node(
    chunk: JobChunk,
    node: Node,
    db: Session
) -> bool:
    """
    Assign a job chunk to a specific node.

    Args:
        chunk: Job chunk to assign
        node: Node to assign to
        db: Database session

    Returns:
        True if assignment successful, False otherwise
    """
    try:
        chunk.assigned_node_id = node.id
        chunk.status = "running"
        db.commit()
        logger.info(f"Assigned chunk {chunk.id} to node {node.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to assign chunk {chunk.id}: {e}")
        db.rollback()
        return False


def schedule_pending_jobs(db: Session) -> int:
    """
    Main scheduling function - assigns pending chunks to available nodes.

    Args:
        db: Database session

    Returns:
        Number of chunks scheduled
    """
    scheduled_count = 0

    # Get all pending chunks
    pending_chunks = db.query(JobChunk).join(Job).filter(
        and_(
            JobChunk.status == 'pending',
            Job.status.in_(['pending', 'running'])
        )
    ).all()

    for chunk in pending_chunks:
        # Get job requirements
        job = db.query(Job).filter(Job.id == chunk.job_id).first()
        if not job:
            continue

        # Find matching offers
        offers = find_matching_offers(
            job.cpu_cores_per_chunk,
            job.ram_gb_per_chunk,
            db
        )

        if offers:
            # Assign to first available node
            node = db.query(Node).filter(Node.id == offers[0].node_id).first()
            if node and assign_chunk_to_node(chunk, node, db):
                scheduled_count += 1

                # Update job status to running if first chunk
                if job.status == 'pending':
                    job.status = 'running'
                    db.commit()

    return scheduled_count
