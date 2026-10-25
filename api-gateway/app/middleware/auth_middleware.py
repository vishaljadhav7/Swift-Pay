from typing import Callable
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.exceptions import InvalidTokenError
from app.services.security_service import security_service
import logging

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for protected routes"""
    
    def __init__(self, app, public_paths: list[str] | None = None):
        super().__init__(app)
        self.public_paths = set(public_paths or [])

    async def dispatch(self, request, call_next : Callable):
        try:
            token = security_service.extract_token_from_header(request.headers.get("Authorization"))
            claims = security_service.decode_token(token)
        except InvalidTokenError as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail}, headers=e.headers)
        except Exception:
            logger.exception("Unexpected error while checking the token")
            return JSONResponse(status_code=500, content={"detail": "Authentication service temporarily unavailable"})

        # outside the try: an error further down is not an authentication error
        request.state.user_id = claims["sub"]
        request.state.role = claims["role"]
        return await call_next(request)
             

    def _is_public_path(self, path: str) -> bool:
        """Exact match, ignoring a trailing slash, so '/' can never match everything."""
        return (path.rstrip("/") or "/") in self.public_paths
