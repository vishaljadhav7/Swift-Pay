from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.notification import NotificationCreate, NotificationResponse
from app.services.notification import notification_service
from app.core.dependencies import get_db
from app.core.auth import CurrentUser, get_current_user, require_admin, ensure_owner_or_admin

router = APIRouter(prefix="/api/v1/notifications", tags=["Notification"])


@router.post("", response_model=NotificationResponse)
async def send_notification(
    data: NotificationCreate,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> NotificationResponse:
    """Send a notification manually (admin only)"""
    return await notification_service.send_notification(db, data)


@router.get("/{user_id}", response_model=List[NotificationResponse])
async def get_notifications_by_user(
    user_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[NotificationResponse]:
    """Get all notifications for a user (the user themselves, or an admin)"""
    ensure_owner_or_admin(user, user_id)
    return await notification_service.get_notifications_by_user_id(db, user_id)