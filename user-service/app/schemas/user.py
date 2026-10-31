from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional

PASSWORD_MIN_LENGTH = 15    # password used as the only factor
PASSWORD_MAX_LENGTH = 64    # allow at least 64
BCRYPT_MAX_BYTES = 72       # bcrypt cannot use more
MIN_UNIQUE_CHARS = 6        # rejects repeating characters 
 
class SignupRequest(BaseModel):
    """User signup request"""
    model_config = ConfigDict(extra="forbid")     # reject unknown fields such as "role"
    
    name: str = Field(..., min_length=1, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        if len(v.encode("utf-8")) > BCRYPT_MAX_BYTES:
            raise ValueError("Password is too long (maximum 72 bytes)")
        if len(set(v)) < MIN_UNIQUE_CHARS:
            raise ValueError("Password is too repetitive (use at least 6 different characters)")
        return v
        
class LoginRequest(BaseModel):
    """No password policy at login: the hash comparison decides"""
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)
    
class UserResponse(BaseModel):
    """User response model"""
    id: str
    name: str
    email: str
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True 
        
class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"           
    
    
class WalletCreateRequest(BaseModel):
    """Request to create wallet"""
    user_id: str
    currency: str = "INR"
    
    
class WalletResponse(BaseModel):
    """Wallet response from wallet service"""
    id: str
    user_id: str
    currency: str
    balance: int
    available_balance: int    