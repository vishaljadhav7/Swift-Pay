from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.notification import NotificationResponse
from app.services.notification import notification_service
from app.core.dependencies import get_db
from app.core.auth import CurrentUser, get_current_user, ensure_owner_or_admin

router = APIRouter(prefix="/api/v1/notifications", tags=["Notification"])


@router.get("/{user_id}", response_model=List[NotificationResponse])
async def get_notifications_by_user(
    user_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[NotificationResponse]:
    """Get all notifications for a user (the user themselves, or an admin)"""
    ensure_owner_or_admin(user, user_id)
    return await notification_service.get_notifications_by_user_id(db, user_id)