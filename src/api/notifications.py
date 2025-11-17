"""Notification configuration endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.extended_models import UserPreference
from src.database.models import User
from src.api.auth import get_current_user

router = APIRouter()


class NotificationConfig(BaseModel):
    """Notification configuration."""
    email: Optional[EmailStr] = None
    webhook_url: Optional[HttpUrl] = None


@router.post("/configure")
async def configure_notifications(
    config: NotificationConfig,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Configure email or webhook notifications for job completion."""
    prefs = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()

    if not prefs:
        prefs = UserPreference(user_id=current_user.id)
        db.add(prefs)

    if config.email:
        prefs.notification_email = str(config.email)
    if config.webhook_url:
        prefs.notification_webhook = str(config.webhook_url)

    db.commit()

    return {"message": "Notifications configured", "email": prefs.notification_email, "webhook": prefs.notification_webhook}


@router.get("/config")
async def get_notification_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current notification configuration."""
    prefs = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()

    return {
        "email": prefs.notification_email if prefs else None,
        "webhook": prefs.notification_webhook if prefs else None
    }
