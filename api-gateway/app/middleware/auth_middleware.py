from typing import Optional, Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.exceptions import InvalidTokenError
from app.services.security_service import security_service
import logging

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for protected routes"""
    
    def __init__(self, app, public_paths: Optional[list] = None):
        super().__init__(app)
        self.public_paths = set(public_paths or [])   

    async def dispatch(self, request, call_next : Callable):
        
        if request.method == "OPTIONS":
            return Response(status_code=200)
        
        if self._is_public_path(request.url.path):
            return await call_next(request)
        
        try:
            authorization = request.headers.get("Authorization")
            token = security_service.extract_token_from_header(authorization=authorization)
            
            # Decode and validate token
            token_data = security_service.decode_token(token)
            user_id = token_data.get("userId")
            email = token_data.get("sub")
            role = token_data.get("role")
            jti = token_data.get("jti")
            
            # Set user info in request state
            request.state.user_id = user_id
            request.state.email = email
            request.state.role = role
            request.state.jti = jti
            
            logger.info(f"Authenticated user: {user_id} ({email})")
            
            return await call_next(request)
        
        except InvalidTokenError as e:
            logger.warning(f"Invalid token: {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        
        except Exception as e:
            logger.error(f"Unexpected error in auth middleware: {e}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Authentication service temporarily unavailable"}
            )
            
             


    def _is_public_path(self, path: str) -> bool:
        """Exact match, ignoring a trailing slash, so '/' can never match everything."""
        return (path.rstrip("/") or "/") in self.public_paths
