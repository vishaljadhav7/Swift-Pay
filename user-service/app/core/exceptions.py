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
        
        
class UserNotFoundException(AppException):
    def __init__(self, resource: str = "User", user_id: str = None):
        detail = f"{resource} not found"
        if user_id:
            detail = f"{resource} with id {user_id} not found"
        super().__init__(detail=detail, status_code=404)        
        
class UserAlreadyExistsException(AppException):
       def __init__(self, email: str = None):
           detail = f"Email already exist"
           if email:
               detail = f"{email} email already exist"
           super().__init__(detail=detail, status_code=409)
                
class InvalidCredentialsError(AppException):
    def __init__(self, detail: str = "Invalid email or password"):
        super().__init__(detail=detail, status_code=401)
                    
class ServiceUnavailableException(AppException):
    def __init__(self, service_name: str):
        super().__init__(
            detail=f"{service_name} service is temporarily unavailable",
            status_code=503
        )                