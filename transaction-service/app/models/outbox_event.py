import uuid6
from datetime import datetime

from sqlalchemy import JSON, DateTime, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.transaction import Base

class OutboxEvent(Base):
    """An event waiting to be sent to Kafka. Saved in the same commit as the business change."""
    
    __tablename__ = "outbox_event"
    __table_args__ = (
        # Only unsent rows are indexed, so the index stays tiny however many events were sent
        Index("ix_outbox_event_unpublished", "created_at", "id", postgresql_where=text("published_at IS NULL")),
    )
    
    id: Mapped[str] = mapped_column(String(36), default=lambda: str(uuid6.uuid7()), primary_key=True, init=False)
    
    topic: Mapped[str] = mapped_column(String(100), nullable=False)
    
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), init=False)
    
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    