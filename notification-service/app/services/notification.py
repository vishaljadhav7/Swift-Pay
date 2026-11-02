"""
Notification Service
Business logic for notifications
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.notification import  NotificationResponse
from app.repositories.notification import notification_repository


class NotificationService:
    """Handles notification business logic"""
    
    async def get_notifications_by_user_id(
        self, 
        db: AsyncSession, 
        user_id: int
    ) -> List[NotificationResponse]:
        """Get all notifications for a user"""
        notifications = await notification_repository.get_by_user_id(db, user_id)
        return [NotificationResponse.from_orm(n) for n in notifications]


notification_service = NotificationService()