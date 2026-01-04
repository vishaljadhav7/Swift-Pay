# import secrets
# from datetime import datetime, timedelta
from typing import Tuple, Dict, Any
from passlib.context import CryptContext
import jwt
from app.core.exceptions import InvalidTokenError
from app.core.config import settings
 
class SecurityService:
    """Handles password hashing and JWT operations"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # def hash_password(self, password : str)-> str :
    #     return self.pwd_context.hash(password)         
    
    # def verify_password(self, plain_password : str , hashed_password) -> bool:
    #     return self.pwd_context.verify(plain_password, hashed_password)
    
    # def create_access_token(self, user_id : str, email: str, role : str) -> Tuple :
        
    #     jti = secrets.token_urlsafe(32)
    #     issued_at = datetime.utcnow()
    #     expires_at = issued_at + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    #     expires_in_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        
    #     payload = {
    #         "sub" : email,
    #         "userId" : user_id,
    #         "role" : role,
    #         "jti" : jti,
    #         "iat" : int(issued_at.timestamp()),
    #         "exp": int(expires_at.timestamp())
    #     }
        
    #     token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
    #     return token, jti, expires_in_seconds
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
            return payload
        except jwt.ExpiredSignatureError:
            raise InvalidTokenError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"Invalid token: {str(e)}")
        
    def extract_token_from_header(self, authorization : str | None) -> str:
        if not authorization:
            raise InvalidTokenError("Missing Authorization header")
        
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise InvalidTokenError("Invalid Authorization header format")
        
        return parts[1]   
    
security_service = SecurityService()
    