"""
Notification Service
Business logic for notifications
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.notification import  NotificationResponse, NotificationCreate
from app.repositories.notification import notification_repository
from app.core.pagination import Page
from app.models.notification import Notification

class NotificationService:
    """Handles notification business logic"""
    
    async def get_notifications_by_user_id(self, db: AsyncSession, user_id: str, limit: int, cursor: str | None) -> Page[NotificationResponse]:
        notifications, next_cursor = await notification_repository.get_by_user_id(db, user_id, limit, cursor)
        return Page(items=[NotificationResponse.from_orm(n) for n in notifications], next_cursor=next_cursor)
    
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


notification_service = NotificationService()