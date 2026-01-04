from datetime import datetime
from sqlalchemy import String, DateTime, Enum as SQLEnum 
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.sql import func
import uuid
import enum

class Roles(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "app_user"
    
    id: Mapped[str] = mapped_column(
        String(20), 
        default=lambda: str(uuid.uuid4()),
        primary_key=True,
        init=False
        )
    
    name: Mapped[str] = mapped_column(
        String(20), 
        nullable=False
        )
    
    email: Mapped[str] = mapped_column(
        String(20), 
        unique=True, 
        index=True,
        nullable=False
        )
    
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    role: Mapped[Roles] = mapped_column(
        SQLEnum(Roles, values_callable=lambda enum: [e.value for e in enum], native_enum=False), 
        default=Roles.USER, 
        nullable=False,
        init=False
        )
    
    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        init=False
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"