from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.notification import NotificationCreate, NotificationResponse
from app.services.notification import notification_service
from app.core.dependencies import get_db

router = APIRouter(prefix="/api/notify", tags=["Notification"])


@router.post("", response_model=NotificationResponse)
async def send_notification(
    data: NotificationCreate,
    db: AsyncSession = Depends(get_db)
) -> NotificationResponse:
    """Send a notification manually"""
    return await notification_service.send_notification(db, data)


@router.get("/{user_id}", response_model=List[NotificationResponse])
async def get_notifications_by_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> List[NotificationResponse]:
    """Get all notifications for a user"""
    return await notification_service.get_notifications_by_user_id(db, user_id)