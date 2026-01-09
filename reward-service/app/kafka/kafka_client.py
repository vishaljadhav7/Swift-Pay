import json
import logging
from typing import Any, Dict, Callable
from aiokafka import AIOKafkaConsumer

logger = logging.getLogger(__name__)

class KafkaConsumerClient:
    """Async Kafka Consumer wrapper"""
    
    def __init__(
        self,
        topic: str,
        group_id: str,
        bootstrap_servers: str = "localhost:9092"
    ):
        self.topic = topic
        self.group_id = group_id
        self.bootstrap_servers = bootstrap_servers
        self.consumer: AIOKafkaConsumer | None = None
    
    async def start(self):
        """Start the Kafka consumer"""
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=self._deserialize_value,
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        await self.consumer.start()
        logger.info(f"Kafka consumer started for topic '{self.topic}' in group '{self.group_id}'")
    
    async def stop(self):
        """Stop the Kafka consumer"""
        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")
    
    async def consume_messages(self, handler: Callable):
        """Consume messages and process with handler"""
        if not self.consumer:
            raise RuntimeError("Consumer not started")
        
        try:
            async for message in self.consumer:
                try:
                    logger.info(f"Received message from topic '{self.topic}': key={message.key}")
                    await handler(message.value)
                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Error in consumer loop: {e}", exc_info=True)
            raise
    
    @staticmethod
    def _deserialize_value(value: bytes) -> Dict[str, Any]:
        """Deserialize JSON value"""
        return json.loads(value.decode('utf-8'))