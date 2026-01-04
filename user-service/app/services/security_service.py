import secrets
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any
from passlib.context import CryptContext
import jwt
from app.core.config import settings
 
class SecurityService:
    """Handles password hashing and JWT operations"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password : str)-> str :
        return self.pwd_context.hash(password)         
    
    def verify_password(self, plain_password : str , hashed_password) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, user_id : str, email: str, role : str) -> Tuple :
        
        jti = secrets.token_urlsafe(32)
        issued_at = datetime.utcnow()
        expires_at = issued_at + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expires_in_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        
        payload = {
            "sub" : email,
            "userId" : user_id,
            "role" : role,
            "jti" : jti,
            "iat" : int(issued_at.timestamp()),
            "exp": int(expires_at.timestamp())
        }
        
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        return token, jti, expires_in_seconds
    
    
security_service = SecurityService()
    