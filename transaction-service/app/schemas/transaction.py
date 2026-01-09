from pydantic import BaseModel, Field
from datetime import datetime

class TransactionCreateRequest(BaseModel):
    sender_id: str = Field(..., min_length=1)
    receiver_id: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    idempotency_key: str = Field(..., min_length=1)  
    
    
class TransactionResponse(BaseModel):
    """Transaction response model"""
    id: str
    sender_id: str
    receiver_id: str
    amount: float
    timestamp: datetime
    status: str
    
    class Config:
        from_attributes = True