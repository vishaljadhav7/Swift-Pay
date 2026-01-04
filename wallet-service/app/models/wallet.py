from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime, Enum as SQLEnum 
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.sql import func
import uuid
import enum

class WalletStatuses(str, enum.Enum):
    ACTIVE = "active"
    CAPTURED = "captured"
    RELEASED = "released"
    
class Base(DeclarativeBase):
    pass


class Wallet(Base):
    __tablename__ = "wallets"
    
    id: Mapped[str] = mapped_column(
        String(20), 
        default=lambda: str(uuid.uuid4()),
        primary_key=True,
        init=False
        )
    
    user_id: Mapped[str] = mapped_column(
        String(50),
        unique=True, 
        nullable=False, 
        index=True
        )
    
    currency: Mapped[str] = mapped_column(
        String(3), 
        default="INR",
        nullable=False
        ) 
    
    balance: Mapped[int] = mapped_column(default=0, nullable=False) 
    
    available_balance: Mapped[int] = mapped_column(default=0, nullable=False)  
    
    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        init=False
    )
    
    updated_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        init=False
    )
    
        # Relationships
    holds: Mapped[list["WalletHold"]] = relationship(back_populates="wallet", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Wallet(id={self.id}, user_id={self.user_id}, balance={self.balance})>"
    
    
    
class WalletHold(Base):
    __tablename__ = "wallet_holds"
    
    id: Mapped[str] = mapped_column(
        String(20), 
        default=lambda: str(uuid.uuid4()),
        primary_key=True,
        init=False
        )
    
    
    wallet_id: Mapped[str] = mapped_column(
        ForeignKey("wallets.id"), 
        nullable=False
    )
    
    hold_reference: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        nullable=False, 
        index=True
        )
    
    amount: Mapped[int] = mapped_column(nullable=False)
    
    status: Mapped[WalletStatuses] = mapped_column(
        SQLEnum(WalletStatuses, values_callable=lambda enum: [e.value for e in enum], native_enum=False), 
        default=WalletStatuses.ACTIVE,
        nullable=False
        ) 

    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        init=False
    )
    
    
    
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
    
    # Relationships
    wallet: Mapped["Wallet"] = relationship(back_populates="holds")
    
    def __repr__(self):
        return f"<WalletHold(id={self.id}, reference={self.hold_reference}, status={self.status})>"    