from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.notification import Notification
from app.core.pagination import paginate

class NotificationRepository:
    """Handles database operations for notifications"""
    
    async def get_by_user_id(self, db: AsyncSession, user_id: str, limit: int, cursor: str | None):
        stmt = select(Notification).where(Notification.user_id == user_id)
        return await paginate(db, stmt, Notification.sent_at, Notification.id, limit, cursor)
    
    async def create(self, db: AsyncSession, notification: Notification) -> Notification:
        """Create a new notification"""
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return notification

notification_repository = NotificationRepository()
