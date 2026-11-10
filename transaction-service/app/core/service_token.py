import time
from pathlib import Path

import jwt
from cryptography.hazmat.primitives import serialization

from app.core.config import settings

CALLER = "transaction-service"   

PRIVATE_KEY = serialization.load_pem_private_key(
    Path(settings.PRIVATE_KEY_PATH).read_bytes(), password=None
) 

def make_service_token(audience: str) -> str:
    """A short-lived token that says: 'this call comes from <this service>'."""
    now = int(time.time())
    return jwt.encode(
        {"iss": CALLER, "aud": audience, "iat": now, "exp": now + 60},
        PRIVATE_KEY,
        algorithm="RS256",
    )