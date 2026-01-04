from pydantic import BaseModel, Field
from typing import Optional


class CreateWalletRequest(BaseModel):
    """Request to create wallet"""
    user_id: str = Field(..., min_length=1)
    currency: str = Field(default="INR", max_length=3)


class CreditRequest(BaseModel):
    """Request to credit wallet"""
    user_id: str = Field(..., min_length=1)
    currency: str = Field(..., max_length=3)
    amount: int = Field(..., gt=0, description="Amount in paise/cents")


class DebitRequest(BaseModel):
    """Request to debit wallet"""
    user_id: str = Field(..., min_length=1)
    currency: str = Field(..., max_length=3)
    amount: int = Field(..., gt=0, description="Amount in paise/cents")


class HoldRequest(BaseModel):
    """Request to place hold on wallet"""
    user_id: str = Field(..., min_length=1)
    currency: str = Field(..., max_length=3)
    amount: int = Field(..., gt=0, description="Amount in paise/cents")


class CaptureRequest(BaseModel):
    """Request to capture a hold"""
    hold_reference: str = Field(..., min_length=1)


class WalletResponse(BaseModel):
    """Wallet response model"""
    id: str
    user_id: str
    currency: str
    balance: int
    available_balance: int
    
    class Config:
        from_attributes = True


class HoldResponse(BaseModel):
    """Hold response model"""
    hold_reference: str
    amount: int
    status: str