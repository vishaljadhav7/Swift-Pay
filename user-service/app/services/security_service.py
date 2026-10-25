import secrets
from datetime import datetime, timedelta, timezone
from typing import Tuple
import jwt
import bcrypt
from app.core.config import settings
from app.core.exceptions import AppException

BCRYPT_ROUNDS = 12        
BCRYPT_MAX_BYTES = 72

class SecurityService:
    """Handles password hashing and JWT operations"""
    
    def hash_password(self, password: str) -> str:
        """Hash with bcrypt (CPU heavy: call it with asyncio.to_thread from async code)"""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode("ascii")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pw = plain_password.encode("utf-8")
        if len(pw) > BCRYPT_MAX_BYTES:       # signup never accepts such a password, so it cannot match
            return False
        try:
            return bcrypt.checkpw(pw, hashed_password.encode("ascii"))
        except ValueError:
            raise AppException("Invalid password hash format", status_code=500)
    
    def create_access_token(self, user_id: str, role: str) -> Tuple[str, str, int]:
        now = datetime.now(timezone.utc)                  
        jti = secrets.token_urlsafe(32)
        expires_in_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        payload = {
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
            "sub": user_id,   
            "role": role,
            "jti": jti,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=expires_in_seconds)).timestamp()),
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token, jti, expires_in_seconds
    

security_service = SecurityService()