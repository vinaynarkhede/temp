"""User preferences endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.extended_models import UserPreference
from src.database.models import User
from src.api.auth import get_current_user

router = APIRouter()


class NodePreferences(BaseModel):
    """Node preference settings."""
    preferred_node_ids: List[int] = []
    avoided_node_ids: List[int] = []


@router.post("/nodes")
async def set_node_preferences(
    prefs: NodePreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set preferred and avoided nodes for job scheduling."""
    user_prefs = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()

    if not user_prefs:
        user_prefs = UserPreference(user_id=current_user.id)
        db.add(user_prefs)

    user_prefs.preferred_node_ids = prefs.preferred_node_ids
    user_prefs.avoided_node_ids = prefs.avoided_node_ids

    db.commit()

    return {"message": "Node preferences updated", "preferred": prefs.preferred_node_ids, "avoided": prefs.avoided_node_ids}


@router.get("/nodes")
async def get_node_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current node preferences."""
    user_prefs = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()

    return {
        "preferred_node_ids": user_prefs.preferred_node_ids if user_prefs else [],
        "avoided_node_ids": user_prefs.avoided_node_ids if user_prefs else []
    }
