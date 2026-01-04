from typing import Tuple, Dict, Any
from passlib.context import CryptContext
import jwt 
from app.core.exceptions import InvalidTokenError
from app.core.config import settings
 
class SecurityService:
    """Handles password hashing and JWT operations"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
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
    