from typing import Any, Dict, Optional

class AppException(Exception):
    """Base exception class for all application exceptions"""
    
    def __init__(
        self,
        detail: str,
        status_code: int = 500,
        headers: Optional[Dict[str, Any]] = None
    ):
        self.detail = detail
        self.status_code = status_code
        self.headers = headers or {}
        super().__init__(self.detail)
        
        
        
class InvalidTokenError(AppException):
    def __init__(self, detail: str = "Authentication required", invalid_token: bool = False):
        challenge = 'Bearer error="invalid_token"' if invalid_token else "Bearer"
        super().__init__(detail=detail, status_code=401, headers={"WWW-Authenticate": challenge})