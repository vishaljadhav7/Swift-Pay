from dataclasses import dataclass
from pathlib import Path

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

PUBLIC_KEY = Path(settings.JWT_PUBLIC_KEY_PATH).read_text()   
bearer = HTTPBearer(auto_error=False)                         


@dataclass(frozen=True)
class CurrentUser:
    id: str
    role: str

    @property
    def is_admin(self) -> bool:
        # exact match: a missing, "None" or misspelled role gets no privileges
        return self.role == "admin"


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> CurrentUser:
    """Who is calling: check the user's JWT here, with the public key. No call to any other service."""
    if credentials is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Not authenticated", headers={"WWW-Authenticate": "Bearer"}
        )
    try:
        claims = jwt.decode(
            credentials.credentials,
            PUBLIC_KEY,
            algorithms=["RS256"],                    # allow-list: the token cannot choose its algorithm
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
            options={"require": ["exp", "iat", "sub", "iss", "aud", "role"]},
        )
    except jwt.InvalidTokenError:                    # expired, bad signature, wrong iss/aud, missing claim...
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid or expired token",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
        )
    return CurrentUser(id=claims["sub"], role=claims["role"])



def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    return user


def ensure_owner_or_admin(user: CurrentUser, *owner_ids: str) -> None:
    if not (user.is_admin or user.id in owner_ids):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You are not allowed to access this resource")