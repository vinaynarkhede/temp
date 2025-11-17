"""
Coordinator main service.

Runs the job scheduler in a loop to assign work to nodes.
"""

import time
import logging
from sqlalchemy.orm import Session

from src.database.connection import get_engine, get_session
from src.coordinator.scheduler import schedule_pending_jobs
from src.utils.logging_config import setup_logging


# Setup logging
logger = setup_logging(__name__)


def run_coordinator(interval_seconds: int = 5):
    """
    Run the coordinator service.

    Args:
        interval_seconds: Seconds between scheduling runs
    """
    logger.info("Starting coordinator service...")

    SessionLocal = get_session()

    while True:
        try:
            db = SessionLocal()
            try:
                # Run scheduler
                scheduled_count = schedule_pending_jobs(db)
                if scheduled_count > 0:
                    logger.info(f"Scheduled {scheduled_count} chunks")
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
