from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


async def domain_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle all domain exceptions"""
    if exc.status_code >= 500:
        logger.error("App exception %s on %s: %s", exc.status_code, request.url.path, exc.detail, exc_info=True)
        detail = "Internal server error"          # do not return internal error text
    else:
        logger.warning("Domain exception %s on %s: %s", exc.status_code, request.url.path, exc.detail)
        detail = exc.detail
    return JSONResponse(status_code=exc.status_code, content={"detail": detail})


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI/Pydantic validation errors"""
    logger.warning("Validation error on %s: %s", request.url.path, exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(exc.errors())},
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle standard HTTP exceptions (this is what carries 401/403 from the auth helper)"""
    logger.warning("HTTP exception on %s: %s", request.url.path, exc.detail)
    detail = exc.detail if isinstance(exc.detail, str) else "An error occurred"
    return JSONResponse(status_code=exc.status_code, content={"detail": detail})


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    logger.error("Unhandled exception on %s", request.url.path, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


def register_exception_handlers(app):
    """Register all exception handlers with FastAPI app"""
    app.add_exception_handler(AppException, domain_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)