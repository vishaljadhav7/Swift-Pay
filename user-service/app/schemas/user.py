from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class SignupRequest(BaseModel):
    """User signup request"""
    name: str = Field(..., min_length=1, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=20)
    admin_key: Optional[str] = None
    
    
class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=20)
    
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
    