from pathlib import Path

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.core.auth import PUBLIC_KEY, bearer
from app.core.config import settings

SERVICE_AUDIENCE = "wallet-service"   # a service token must be made FOR the wallet

# Public key of every service that is allowed to call the wallet, by service name.
CALLER_KEYS = {
    "transaction-service": Path(settings.TRANSACTION_SERVICE_PUBLIC_KEY_PATH).read_text(),
    "user-service": PUBLIC_KEY,   
}


def allow_callers(*allowed: str):
    """Dependency: the request must carry a valid service token from one of the allowed services."""

    def check(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str:
        unauthorized = HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Invalid service credentials", headers={"WWW-Authenticate": "Bearer"}
        )
        if credentials is None:
            raise unauthorized
        try:
            # Read the caller name only to pick which public key to verify with. It is NOT trusted yet.
            caller = jwt.decode(credentials.credentials, options={"verify_signature": False}).get("iss")
            key = CALLER_KEYS.get(caller) if isinstance(caller, str) else None
            if key is None:
                raise unauthorized
            jwt.decode(
                credentials.credentials,
                key,
                algorithms=["RS256"],
                audience=SERVICE_AUDIENCE,
                issuer=caller,
                options={"require": ["exp", "iat", "iss", "aud"]},
            )
        except jwt.InvalidTokenError:
            raise unauthorized
        if caller not in allowed:   # a known service, but not allowed on this endpoint
            raise HTTPException(status.HTTP_403_FORBIDDEN, "This service may not call this endpoint")
        return caller

    return check