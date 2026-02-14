"""
Notification Service
Business logic for notifications
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.repositories.notification import notification_repository


class NotificationService:
    """Handles notification business logic"""
    
    async def send_notification(
        self, 
        db: AsyncSession, 
        data: NotificationCreate
    ) -> NotificationResponse:
        """Send a notification"""
        notification = Notification(
            user_id=data.user_id,
            message=data.message
        )
        created = await notification_repository.create(db, notification)
        return NotificationResponse.from_orm(created)
    
    async def get_notifications_by_user_id(
        self, 
        db: AsyncSession, 
        user_id: int
    ) -> List[NotificationResponse]:
        """Get all notifications for a user"""
        notifications = await notification_repository.get_by_user_id(db, user_id)
        return [NotificationResponse.from_orm(n) for n in notifications]


notification_service = NotificationService()