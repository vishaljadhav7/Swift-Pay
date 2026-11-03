from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.notification import NotificationResponse
from app.services.notification import notification_service
from app.core.dependencies import get_db
from app.core.auth import CurrentUser, get_current_user, ensure_owner_or_admin
from app.core.pagination import Page, DEFAULT_LIMIT, MAX_LIMIT

router = APIRouter(prefix="/api/v1/notifications", tags=["Notification"])


@router.get("/{user_id}", response_model=Page[NotificationResponse])
async def get_notifications_by_user(
    user_id: str,
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    cursor: str | None = None,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Page[NotificationResponse]:
    ensure_owner_or_admin(user, user_id)
    return await notification_service.get_notifications_by_user_id(db, user_id, limit, cursor)