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

class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(detail=detail, status_code=400)        
        
        
class ForbiddenException(AppException):
    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(detail=detail, status_code=403)
        

class TransactionNotFoundException(AppException):
    def __init__(self, transaction_id: str = None):
        detail = f"transaction not found"
        if transaction_id:
            detail = f"transaction with id {transaction_id} not found"
        super().__init__(detail=detail, status_code=404)        
        
        
class ServiceUnavailableException(AppException):
    def __init__(self, service_name: str):
        super().__init__(
            detail=f"{service_name} service is temporarily unavailable",
            status_code=503
        )        