from fastapi import FastAPI

from contextlib import asynccontextmanager
import logging
from app.core.seed import seed_admin
from app.core.config import settings
from app.core.database import close_db, init_db
from app.controllers.user import router as user_router
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME}...")
    await init_db()
    logger.info("Database initialized")
    await seed_admin()
    yield
    # Shutdown
    logger.info("Shutting down...")
    await close_db()
    logger.info("Database connections closed")



app = FastAPI(
    title="User Service",
    description="User management and authentication service",
    version="1.0.0",
    lifespan=lifespan
)




# global exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    if exc.status_code == 500:   # repository errors carry raw DB error text: log it, don't return it
        logger.error("App exception on %s: %s", request.url.path, exc.detail)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=exc.headers)

# Include routers
app.include_router(user_router)



@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": settings.SERVICE_NAME,
        "status": "running",
        "port": settings.SERVICE_PORT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=True
    )