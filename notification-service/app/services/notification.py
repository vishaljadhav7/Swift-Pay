"""
Notification Service
Business logic for notifications
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.notification import  NotificationResponse
from app.repositories.notification import notification_repository
from app.core.pagination import Page

class NotificationService:
    """Handles notification business logic"""
    
    async def get_notifications_by_user_id(self, db: AsyncSession, user_id: str, limit: int, cursor: str | None) -> Page[NotificationResponse]:
        notifications, next_cursor = await notification_repository.get_by_user_id(db, user_id, limit, cursor)
        return Page(items=[NotificationResponse.from_orm(n) for n in notifications], next_cursor=next_cursor)


notification_service = NotificationService()