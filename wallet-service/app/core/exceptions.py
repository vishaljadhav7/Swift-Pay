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
        
        
class ConflictException(AppException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(detail=detail, status_code=409)        
        
class WalletNotFoundException(AppException):
    def __init__(self, user_id: str = None):
        detail = "wallet not found"
        if user_id:
            detail = f"wallet with id {user_id} not found"
        super().__init__(detail=detail, status_code=404) 
        
class HoldNotFoundException(AppException):
    def __init__(self, hold_reference: str):
        detail = "wallet hold not found"
        if hold_reference:
            detail = f"wallet holde with id {hold_reference} not found"
        super().__init__(detail=detail, status_code=404)              
        
        
# 400 - Bad Request
class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(detail=detail, status_code=400)


class InsufficientFundsException(AppException):
    def __init__(self, detail: str = "Insufficient funds"):
        super().__init__(detail=detail, status_code=400)        