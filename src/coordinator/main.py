"""
Coordinator main service.

Runs the job scheduler in a loop to assign work to nodes.
"""

import time
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.connection import get_engine, get_session
from src.coordinator.scheduler import schedule_pending_jobs
from src.coordinator.fault_tolerance import reallocate_orphaned_chunks, check_job_completion
from src.database.models import Node
from src.utils.logging_config import setup_logging


# Setup logging
logger = setup_logging(__name__)


# Node heartbeat timeout in seconds
NODE_TIMEOUT_SECONDS = 90


def check_node_health(db: Session, timeout_seconds: int = NODE_TIMEOUT_SECONDS) -> int:
    """
    Check node heartbeats and mark dead nodes as offline.

    Args:
        db: Database session
        timeout_seconds: Heartbeat timeout in seconds

    Returns:
        Number of nodes marked offline
    """
    timeout_threshold = datetime.now() - timedelta(seconds=timeout_seconds)

    # Find online nodes with stale heartbeats
    stale_nodes = db.query(Node).filter(
        Node.status == 'online',
        Node.last_heartbeat < timeout_threshold
    ).all()

    for node in stale_nodes:
        node.status = 'offline'
        logger.warning(f"Node {node.id} ({node.name}) marked offline - no heartbeat")

    if stale_nodes:
        db.commit()

    return len(stale_nodes)


def run_coordinator(interval_seconds: int = 5):
    """
    Run the coordinator service.

    Performs:
    1. Node health checking
    2. Orphaned chunk reallocation
    3. Job scheduling
    4. Job completion checking

    Args:
        interval_seconds: Seconds between coordination runs
    """
    logger.info("Starting coordinator service...")

    SessionLocal = get_session()

    while True:
        try:
            db = SessionLocal()
            try:
                # 1. Check node health
                offline_count = check_node_health(db)
                if offline_count > 0:
                    logger.info(f"Marked {offline_count} nodes offline")

                # 2. Reallocate orphaned chunks
                reallocated_count = reallocate_orphaned_chunks(db)
                if reallocated_count > 0:
                    logger.info(f"Reallocated {reallocated_count} orphaned chunks")

                # 3. Schedule pending chunks
                scheduled_count = schedule_pending_jobs(db)
                if scheduled_count > 0:
                    logger.info(f"Scheduled {scheduled_count} chunks")

                # 4. Check for completed jobs
                completed_count = check_job_completion(db)
                if completed_count > 0:
                    logger.info(f"Completed {completed_count} jobs")

            finally:
                db.close()

            # Sleep before next iteration
            time.sleep(interval_seconds)

        except KeyboardInterrupt:
            logger.info("Coordinator shutting down...")
            break
        except Exception as e:
            logger.error(f"Coordinator error: {e}")
            time.sleep(interval_seconds)


if __name__ == "__main__":
    run_coordinator()
