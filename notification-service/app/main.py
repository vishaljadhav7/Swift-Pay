from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from app.core.config import settings
from app.core.database import init_db, close_db
from app.controllers.notification import router as notification_router
# from app.middleware.exception_handler import ExceptionHandlerMiddleware
from app.kafka.kafka_client import KafkaConsumerClient
from app.kafka.notification_consumer import notification_consumer


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Kafka consumer
kafka_consumer = KafkaConsumerClient(
    topic="txn-initiated",
    group_id="notification-group",
    bootstrap_servers="localhost:9092"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME}...")
    await init_db()
    logger.info("Database initialized")
    
    # Start Kafka consumer in background
    await kafka_consumer.start()
    consumer_task = asyncio.create_task(
        kafka_consumer.consume_messages(notification_consumer.handle_transaction_event)
    )
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    consumer_task.cancel()
    await kafka_consumer.stop()
    await close_db()
    logger.info("Shutdown complete")


app = FastAPI(
    title="Notification Service",
    description="Notification service with Kafka consumer",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware(ExceptionHandlerMiddleware)

app.include_router(notification_router)


@app.get("/")
async def root():
    """Health check"""
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