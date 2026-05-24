import json
import logging
from typing import Any, Dict, Callable
from datetime import datetime
from aiokafka import AIOKafkaProducer

logger = logging.getLogger(__name__)

class KafkaProducerClient:
    """Async Kafka Producer wrapper"""
    
    def __init__(self, bootstrap_servers: str = "kafka:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.producer: AIOKafkaProducer | None = None
    
    async def start(self):
        """Start the Kafka producer"""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=self._serialize_value,
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        await self.producer.start()
        logger.info("Kafka producer started")
    
    async def stop(self):
        """Stop the Kafka producer"""
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")
    
    async def send_message(self, topic: str, key: str, value: Dict[str, Any]):
        """Send message to Kafka topic"""
        if not self.producer:
            raise RuntimeError("Producer not started")
        
        try:
            await self.producer.send_and_wait(topic, value=value, key=key)
            logger.info(f"Message sent to topic '{topic}' with key '{key}'")
        except Exception as e:
            logger.error(f"Failed to send message to Kafka: {e}")
            raise
    
    @staticmethod
    def _serialize_value(value: Dict[str, Any]) -> bytes:
        """Serialize value with datetime handling"""
        def default_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        return json.dumps(value, default=default_serializer).encode('utf-8')