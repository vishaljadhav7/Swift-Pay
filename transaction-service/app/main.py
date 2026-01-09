from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import init_db, close_db
from app.utils.kafka_client import KafkaProducerClient
from app.services.transaction import transaction_service
from app.controller.transaction import router as transaction_router


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Kafka producer
kafka_producer = KafkaProducerClient(bootstrap_servers="localhost:9092")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events - startup and shutdown"""
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME}...")
    await init_db()
    logger.info("Database initialized")
    
    # Start Kafka producer
    await kafka_producer.start()
    transaction_service.set_kafka_producer(kafka_producer)
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await kafka_producer.stop()
    await close_db()
    logger.info("Shutdown complete")
    
    
app = FastAPI(
    title="Transaction Service",
    description="Money transfer orchestration service",
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
app.include_router(transaction_router)


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