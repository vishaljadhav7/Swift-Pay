from datetime import datetime
from sqlalchemy import String, Text, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, MappedAsDataclass

import uuid6
from sqlalchemy.sql import func


class Base(DeclarativeBase, MappedAsDataclass): 
    pass
    
class Notification(Base):
    __tablename__ = "notifications"
    
    id: Mapped[str] = mapped_column(
        String(36), 
        default=lambda: str(uuid6.uuid7()),
        primary_key=True,
        init=False
        )
    
    
    user_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False, 
        index=True
        )
    
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        init=False
    )
    
    __table_args__ = (
        Index("ix_notifications_user_sent", "user_id", "sent_at", "id"),
    )

    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id})>"