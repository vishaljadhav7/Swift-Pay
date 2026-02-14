from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.models.notification import Notification


class NotificationRepository:
    """Handles database operations for notifications"""
    
    async def create(self, db: AsyncSession, notification: Notification) -> Notification:
        """Create a new notification"""
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return notification
    
    async def get_by_user_id(self, db: AsyncSession, user_id: str) -> List[Notification]:
        """Get all notifications for a user"""
        stmt = select(Notification).where(
            Notification.user_id == user_id
        ).order_by(Notification.sent_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())


notification_repository = NotificationRepository()
