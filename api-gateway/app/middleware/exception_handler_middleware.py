from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Union

from app.core.exceptions import AppException, InvalidTokenError

logger = logging.getLogger(__name__)


class ErrorResponse:
    def __init__(
        self,
        error_code: str,
        message: str,
        details: dict = None,
        status_code: int= 500
        ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        
    def to_dict(self):
        response = {
            "error" : {
                "code" : self.error_code,
                "message" : self.message
            }
        }
        if self.details:
            response["error"]["details"] = self.details
        return response       
    
def map_exception_to_status_code(exc: AppException) -> int:   
    pass