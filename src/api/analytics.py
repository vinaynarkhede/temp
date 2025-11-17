"""Analytics and statistics endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.database.connection import get_db
from src.database.models import Job, Node, User, CreditTransaction
from src.api.auth import get_current_user

router = APIRouter()


@router.get("/user")
async def get_user_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for current user."""
    jobs_submitted = db.query(func.count(Job.id)).filter(Job.owner_id == current_user.id).scalar()

    total_spent = db.query(func.sum(CreditTransaction.amount)).filter(
        CreditTransaction.from_user_id == current_user.id
    ).scalar() or 0

    return {
        "jobs_submitted": jobs_submitted,
        "total_credits_spent": abs(total_spent),
        "current_balance": current_user.credit_balance,
        "username": current_user.username
    }


@router.get("/marketplace")
async def get_marketplace_stats(db: Session = Depends(get_db)):
    """Get public marketplace statistics."""
    total_nodes = db.query(func.count(Node.id)).scalar()
    online_nodes = db.query(func.count(Node.id)).filter(Node.status == 'online').scalar()
    total_jobs = db.query(func.count(Job.id)).scalar()
    completed_jobs = db.query(func.count(Job.id)).filter(Job.status == 'completed').scalar()

    total_cpu = db.query(func.sum(Node.cpu_cores)).scalar() or 0
    total_ram = db.query(func.sum(Node.ram_gb)).scalar() or 0

    return {
        "total_nodes": total_nodes,
        "online_nodes": online_nodes,
        "total_cpu_cores": total_cpu,
        "total_ram_gb": total_ram,
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs
    }
