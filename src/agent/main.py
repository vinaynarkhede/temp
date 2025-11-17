"""
Node agent main service.

Runs on friend PCs to:
1. Send heartbeats to coordinator
2. Pull assigned job chunks
3. Execute chunks in Docker containers
4. Report results back
"""

import time
import logging
import argparse
from datetime import datetime
from sqlalchemy.orm import Session

from src.database.connection import get_session
from src.database.models import Node, JobChunk
from src.utils.logging_config import setup_logging


logger = setup_logging(__name__)


def send_heartbeat(node_id: int, db: Session) -> bool:
    """Send heartbeat to update node status."""
    try:
        node = db.query(Node).filter(Node.id == node_id).first()
        if node:
            node.last_heartbeat = datetime.now()
            node.status = 'online'
            db.commit()
            return True
    except Exception as e:
        logger.error(f"Heartbeat failed: {e}")
        db.rollback()
    return False


def pull_assigned_chunks(node_id: int, db: Session):
    """Get chunks assigned to this node."""
    return db.query(JobChunk).filter(
        JobChunk.assigned_node_id == node_id,
        JobChunk.status == 'running'
    ).all()


def execute_chunk(chunk: JobChunk, db: Session) -> bool:
    """
    Execute a job chunk.
    
    Simplified: marks chunk as completed immediately.
    In production: would run Docker container and wait for completion.
    """
    try:
        # Mark as completed (simplified)
        chunk.status = 'completed'
        chunk.completed_at = datetime.now()
        db.commit()
        logger.info(f"Completed chunk {chunk.id}")
        return True
    except Exception as e:
        logger.error(f"Chunk execution failed: {e}")
        chunk.status = 'failed'
        chunk.retry_count += 1
        db.commit()
        return False


def run_agent(node_id: int, heartbeat_interval: int = 10):
    """Run the node agent service."""
    logger.info(f"Starting node agent for node {node_id}...")
    
    SessionLocal = get_session()
    
    while True:
        try:
            db = SessionLocal()
            try:
                # Send heartbeat
                send_heartbeat(node_id, db)
                
                # Pull and execute assigned chunks
                chunks = pull_assigned_chunks(node_id, db)
                for chunk in chunks:
                    execute_chunk(chunk, db)
                
            finally:
                db.close()
            
            time.sleep(heartbeat_interval)
            
        except KeyboardInterrupt:
            logger.info("Agent shutting down...")
            break
        except Exception as e:
            logger.error(f"Agent error: {e}")
            time.sleep(heartbeat_interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--node-id", type=int, required=True)
    args = parser.parse_args()
    
    run_agent(args.node_id)
