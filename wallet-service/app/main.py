from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.controller.wallet import router as wallet_router
from app.core.database import init_db, close_db
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events - startup and shutdown"""
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME}...")
    await init_db()
    logger.info("Database initialized")
    
    # Start hold expiry scheduler
    # await hold_expiry_scheduler.start()
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    # await hold_expiry_scheduler.stop()
    await close_db()
    logger.info("Shutdown complete")
    
    
    
# Create FastAPI app
app = FastAPI(
    title="Wallet Service",
    description="Wallet management with holds and transactions",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # Add global exception handler
# app.add_middleware(ExceptionHandlerMiddleware)

# # Include routers
app.include_router(wallet_router)


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