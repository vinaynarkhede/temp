"""
Node affinity rules for optimizing chunk placement.

Keeps related chunks together to reduce data transfer and improve locality.
"""

import logging
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.database.models import Job, JobChunk, Node

logger = logging.getLogger(__name__)


class AffinityRule:
    """Defines how chunks should be distributed across nodes."""

    def __init__(
        self,
        job_id: int,
        strategy: str = "spread",
        preferred_region: Optional[str] = None,
        preferred_node_ids: Optional[List[int]] = None,
        keep_chunks_together: bool = False
    ):
        """
        Initialize affinity rule.

        Args:
            job_id: Job ID this rule applies to
            strategy: Distribution strategy
                - "spread": Distribute across different nodes (default)
                - "pack": Pack onto fewest nodes possible
                - "region": Prefer nodes in specific region
                - "node": Prefer specific nodes
            preferred_region: Preferred geographic region
            preferred_node_ids: List of preferred node IDs
            keep_chunks_together: If True, try to run all chunks on same node
        """
        self.job_id = job_id
        self.strategy = strategy
        self.preferred_region = preferred_region
        self.preferred_node_ids = preferred_node_ids or []
        self.keep_chunks_together = keep_chunks_together


class AffinityScheduler:
    """Scheduler that respects affinity rules."""

    def __init__(self, db: Session):
        self.db = db
        self.affinity_rules: Dict[int, AffinityRule] = {}

    def add_rule(self, rule: AffinityRule) -> None:
        """Add an affinity rule for a job."""
        self.affinity_rules[rule.job_id] = rule
        logger.info(f"Added affinity rule for job {rule.job_id}: {rule.strategy}")

    def get_rule(self, job_id: int) -> Optional[AffinityRule]:
        """Get affinity rule for a job."""
        return self.affinity_rules.get(job_id)

    def select_node_for_chunk(
        self,
        chunk: JobChunk,
        available_nodes: List[Node]
    ) -> Optional[Node]:
        """
        Select best node for chunk based on affinity rules.

        Args:
            chunk: Job chunk to schedule
            available_nodes: List of available nodes

        Returns:
            Selected node or None if no suitable node
        """
        rule = self.get_rule(chunk.job_id)

        if not rule:
            # No rule, use default selection (first available)
            return available_nodes[0] if available_nodes else None

        # Apply strategy
        if rule.strategy == "pack":
            return self._pack_strategy(chunk, available_nodes)
        elif rule.strategy == "spread":
            return self._spread_strategy(chunk, available_nodes)
        elif rule.strategy == "region":
            return self._region_strategy(chunk, available_nodes, rule.preferred_region)
        elif rule.strategy == "node":
            return self._node_preference_strategy(chunk, available_nodes, rule.preferred_node_ids)
        else:
            return available_nodes[0] if available_nodes else None

    def _pack_strategy(self, chunk: JobChunk, available_nodes: List[Node]) -> Optional[Node]:
        """
        Pack chunks onto fewest nodes (data locality).

        Prefer nodes that already have chunks from this job.
        """
        # Find nodes already running chunks from this job
        existing_assignments = self.db.query(JobChunk).filter(
            and_(
                JobChunk.job_id == chunk.job_id,
                JobChunk.status == 'running',
                JobChunk.assigned_node_id.isnot(None)
            )
        ).all()

        if existing_assignments:
            # Get nodes already running this job's chunks
            used_node_ids = set(c.assigned_node_id for c in existing_assignments)
            for node in available_nodes:
                if node.id in used_node_ids:
                    logger.info(f"Packing chunk {chunk.id} onto already-used node {node.id}")
                    return node

        # No existing assignments, use first available
        return available_nodes[0] if available_nodes else None

    def _spread_strategy(self, chunk: JobChunk, available_nodes: List[Node]) -> Optional[Node]:
        """
        Spread chunks across different nodes (load balancing).

        Prefer nodes NOT already running this job's chunks.
        """
        # Find nodes already running chunks from this job
        existing_assignments = self.db.query(JobChunk).filter(
            and_(
                JobChunk.job_id == chunk.job_id,
                JobChunk.status == 'running',
                JobChunk.assigned_node_id.isnot(None)
            )
        ).all()

        used_node_ids = set(c.assigned_node_id for c in existing_assignments)

        # Prefer unused nodes
        for node in available_nodes:
            if node.id not in used_node_ids:
                logger.info(f"Spreading chunk {chunk.id} to unused node {node.id}")
                return node

        # All nodes used, use first available
        return available_nodes[0] if available_nodes else None

    def _region_strategy(
        self,
        chunk: JobChunk,
        available_nodes: List[Node],
        preferred_region: Optional[str]
    ) -> Optional[Node]:
        """Prefer nodes in specific region."""
        if not preferred_region:
            return available_nodes[0] if available_nodes else None

        # NOTE: Requires Node model to have 'region' field
        # For now, fallback to first available
        # In production, would filter: nodes_in_region = [n for n in available_nodes if n.region == preferred_region]
        logger.info(f"Region affinity requested: {preferred_region} (not yet implemented)")
        return available_nodes[0] if available_nodes else None

    def _node_preference_strategy(
        self,
        chunk: JobChunk,
        available_nodes: List[Node],
        preferred_node_ids: List[int]
    ) -> Optional[Node]:
        """Prefer specific nodes."""
        # Try preferred nodes first
        for node in available_nodes:
            if node.id in preferred_node_ids:
                logger.info(f"Using preferred node {node.id} for chunk {chunk.id}")
                return node

        # No preferred node available, use any
        return available_nodes[0] if available_nodes else None


def create_affinity_rule_from_job(job: Job, db: Session) -> AffinityRule:
    """
    Auto-create affinity rule based on job characteristics.

    Args:
        job: Job to create rule for
        db: Database session

    Returns:
        Recommended affinity rule
    """
    # Large jobs (many chunks) benefit from packing (data locality)
    if job.total_chunks >= 10:
        strategy = "pack"
        logger.info(f"Job {job.id} has {job.total_chunks} chunks, using 'pack' strategy")
    # Small jobs benefit from spreading (parallelization)
    else:
        strategy = "spread"
        logger.info(f"Job {job.id} has {job.total_chunks} chunks, using 'spread' strategy")

    return AffinityRule(
        job_id=job.id,
        strategy=strategy,
        keep_chunks_together=job.total_chunks >= 10
    )
