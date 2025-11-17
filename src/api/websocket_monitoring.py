"""Real-time job monitoring via WebSocket."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import asyncio
import json

from src.database.connection import get_db
from src.database.models import Job, JobChunk

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, job_id: int):
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = []
        self.active_connections[job_id].append(websocket)

    def disconnect(self, websocket: WebSocket, job_id: int):
        if job_id in self.active_connections:
            self.active_connections[job_id].remove(websocket)

    async def send_update(self, job_id: int, message: dict):
        if job_id in self.active_connections:
            for connection in self.active_connections[job_id]:
                await connection.send_text(json.dumps(message))


manager = ConnectionManager()


@router.websocket("/jobs/{job_id}")
async def job_progress_websocket(websocket: WebSocket, job_id: int):
    """
    WebSocket endpoint for real-time job progress updates.

    Sends updates every 2 seconds with current progress.
    """
    await manager.connect(websocket, job_id)

    try:
        while True:
            # This is a simplified version - in production, use pub/sub
            from src.database.connection import get_engine, get_session
            SessionLocal = get_session()
            db = SessionLocal()

            try:
                job = db.query(Job).filter(Job.id == job_id).first()
                if not job:
                    await websocket.send_text(json.dumps({"error": "Job not found"}))
                    break

                chunks = db.query(JobChunk).filter(JobChunk.job_id == job_id).all()
                chunk_statuses = {
                    "pending": sum(1 for c in chunks if c.status == "pending"),
                    "running": sum(1 for c in chunks if c.status == "running"),
                    "completed": sum(1 for c in chunks if c.status == "completed"),
                    "failed": sum(1 for c in chunks if c.status == "failed")
                }

                progress = {
                    "job_id": job_id,
                    "status": job.status,
                    "progress_percent": (job.completed_chunks / job.total_chunks * 100) if job.total_chunks > 0 else 0,
                    "completed_chunks": job.completed_chunks,
                    "total_chunks": job.total_chunks,
                    "chunk_statuses": chunk_statuses
                }

                await websocket.send_text(json.dumps(progress))

                # Exit if job is complete
                if job.status in ["completed", "failed"]:
                    break

            finally:
                db.close()

            await asyncio.sleep(2)  # Update every 2 seconds

    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
