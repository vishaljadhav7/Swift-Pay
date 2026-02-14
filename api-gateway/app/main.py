from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.rate_limiter_middleware import RateLimiter, RateLimiterMiddleware
# from app.middleware.exception_handler import ExceptionHandlerMiddleware
from app.services.proxy_service import proxy_service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="API Gateway",
    description="Central API Gateway for Swift-Pay microservices",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add global exception handler
# app.add_middleware(ExceptionHandlerMiddleware)


rate_limiter = RateLimiter(
    replenish_rate=settings.RATE_LIMIT_REPLENISH_RATE,
    burst_capacity=settings.RATE_LIMIT_BURST_CAPACITY
)

app.add_middleware(RateLimiterMiddleware, rate_limiter=rate_limiter)

app.add_middleware(AuthMiddleware, protected_paths=settings.PROTECTED_PATHS)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": settings.SERVICE_NAME,
        "status": "running",
        "port": settings.SERVICE_PORT
    }
    
    
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):
    """
    Proxy all requests to backend microservices
    """
    return await proxy_service.proxy_request(request)    



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=True
    )