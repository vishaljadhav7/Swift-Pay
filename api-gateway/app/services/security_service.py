from typing import Dict, Any
import jwt 
import logging
from app.core.exceptions import InvalidTokenError
from app.core.config import settings
 
logger = logging.getLogger(__name__) 
 
class SecurityService:
    """Verifies JWT access tokens"""

    def decode_token(self, token: str) -> Dict[str, Any]:
        try:
            return jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],          # the token cannot choose its algorithm
                audience=settings.JWT_AUDIENCE,
                issuer=settings.JWT_ISSUER,
                options={"require": ["exp", "iat", "sub", "iss", "aud", "role"]},
            )
        except jwt.InvalidTokenError as e:
            logger.warning("Rejected token: %s", type(e).__name__)   # reason stays in the log
            raise InvalidTokenError("Invalid or expired token", invalid_token=True)

    def extract_token_from_header(self, authorization: str | None) -> str:
        parts = authorization.split() if authorization else []
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise InvalidTokenError("Authentication required")
        return parts[1]
    
security_service = SecurityService()
    