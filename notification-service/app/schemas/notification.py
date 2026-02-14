from pydantic import BaseModel
from datetime import datetime


class NotificationCreate(BaseModel):
    """Request to create notification"""
    user_id: str
    message: str


class NotificationResponse(BaseModel):
    """Notification response model"""
    id: str
    user_id: str
    message: str
    sent_at: datetime
    
    class Config:
        from_attributes = True


class TransactionEvent(BaseModel):
    """Transaction event from Kafka"""
    id: str
    sender_id: str
    receiver_id: str
    amount: float
    timestamp: str
    status: str