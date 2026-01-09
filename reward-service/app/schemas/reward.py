from pydantic import BaseModel
from datetime import datetime


class RewardResponse(BaseModel):
    """Reward response model"""
    id: int
    user_id: int
    points: float
    sent_at: datetime
    transaction_id: int
    
    class Config:
        from_attributes = True


class TransactionEvent(BaseModel):
    """Transaction event from Kafka"""
    id: int
    sender_id: int
    receiver_id: int
    amount: float
    timestamp: str
    status: str