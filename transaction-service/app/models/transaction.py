from datetime import datetime
from sqlalchemy import String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, MappedAsDataclass
import uuid
import enum
from sqlalchemy.sql import func


class TransactionStatuses(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class Base(DeclarativeBase, MappedAsDataclass):
    pass


class Transaction(Base):
    __tablename__ = "transaction"
    
    id: Mapped[str] = mapped_column(
        String(36), 
        default=lambda: str(uuid.uuid4()),
        primary_key=True,
        init=False
        )
    
    sender_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False, 
        index=True
        )
    
    receiver_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False, 
        index=True
        )
    
    amount: Mapped[float] = mapped_column(nullable=False)
    
    idempotency_key: Mapped[str] = mapped_column(nullable=False, index=True)
    
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        init=False
    )
    
    status: Mapped[TransactionStatuses] = mapped_column(
        SQLEnum(TransactionStatuses, values_callable=lambda enum: [e.value for e in enum], native_enum=False), 
        default=TransactionStatuses.PENDING, 
        nullable=False
        )
    

    
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, sender={self.sender_id}, receiver={self.receiver_id}, status={self.status})>"