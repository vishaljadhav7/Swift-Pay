from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, MappedAsDataclass
import uuid
from sqlalchemy.sql import func

class Base(DeclarativeBase, MappedAsDataclass):
    pass


class Reward(Base):
    __tablename__ = "reward"
    
    id: Mapped[str] = mapped_column(
        String(36), 
        default=lambda: str(uuid.uuid4()),
        primary_key=True,
        init=False
        )
    
    
    user_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False, 
        index=True
        )
    
    points: Mapped[float] = mapped_column(nullable=False)

    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        init=False
    )

    transaction_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False, 
        index=True
        )
    
    def __repr__(self):
        return f"<Reward(id={self.id}, user_id={self.user_id}, points={self.points})>"