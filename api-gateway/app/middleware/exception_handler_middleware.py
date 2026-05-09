from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from app.core.exceptions import (
    AppException
)         

logger = logging.getLogger(__name__)

class ErrorResponse:
    """Standardized error response format"""
    def __init__(
        self,
        detail: str, 
        status_code: int = 500
    ):
        self.detail = detail
        self.status_code = status_code

    def to_dict(self):
        response = {
            "error": {
                "code": self.status_code,
                "detail": self.detail,
            }
        }
        return response


     
async def domain_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle all domain exceptions"""
    status_code = exc.status_code 
    
    
    # Log based on severity
    if status_code >= 500:
        logger.error(
            f"App exception: {exc.status_code}",
            extra={
                "detail": exc.detail,
                "path": request.url.path,
            },
            exc_info=True
        )
    else:
        logger.warning(
            f"Domain exception: {exc.status_code}",
            extra={
                "status_code": exc.status_code,
                "detail": exc.detail,
                "path": request.url.path,
            }
        )
    
    error_response = ErrorResponse(
        detail=exc.detail,
        status_code=status_code
    )
    
    return JSONResponse(
        status_code=status_code,
        content=error_response.detail
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI/Pydantic validation errors"""
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}") 
    
    error_response = ErrorResponse(
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        details={"errors": exc.errors()},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.to_dict()
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle standard HTTP exceptions"""
    logger.warning(f"HTTP exception on {request.url.path}: {exc.detail}")
    
    error_response = ErrorResponse(
        message=exc.detail if isinstance(exc.detail, str) else "An error occurred",
        status_code=exc.status_code
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.detail
    )
    
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    logger.error(
        f"Unhandled exception on {request.url.path}",
        exc_info=True,
        extra={"path": request.url.path, "method": request.method}
    )
    
    error_response = ErrorResponse(
        message="An unexpected error occurred. Please try again later.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response
    )    
    

def register_exception_handlers(app):
    """Register all exception handlers with FastAPI app"""
    app.add_exception_handler(AppException, domain_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)