import asyncio
import json
import logging
from typing import Any, Dict, Callable

from aiokafka import AIOKafkaConsumer
from aiokafka.structs import TopicPartition

logger = logging.getLogger(__name__)

RETRY_DELAY_SECONDS = 1
MAX_RETRY_DELAY_SECONDS = 30

class KafkaConsumerClient:
    """Async Kafka Consumer wrapper"""
    
    def __init__(
        self,
        topic: str,
        group_id: str,
        bootstrap_servers: str = "kafka:9092"
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
            auto_offset_reset="earliest",
            enable_auto_commit=False  # Manual offset commits
        )
        await self.consumer.start()
        logger.info(f"Kafka consumer started for topic '{self.topic}' in group '{self.group_id}'")
    
    async def stop(self):
        """Stop the Kafka consumer"""
        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")
    
    async def consume_messages(self, handler: Callable):
        """Process messages and commit offsets only after successful handling"""
        if not self.consumer:
            raise RuntimeError("Consumer not started")

        try:
            async for message in self.consumer:
                retry_delay = RETRY_DELAY_SECONDS

                while True:
                    try:
                        # 1. Process the event and persist its business result
                        await handler(message.value)

                        # 2. Commit only this message's next offset
                        topic_partition = TopicPartition(message.topic, message.partition)
                        await self.consumer.commit({topic_partition: message.offset + 1})

                        logger.info(
                            f"Successfully processed and committed "
                            f"topic={message.topic}, "
                            f"partition={message.partition}, "
                            f"offset={message.offset}"
                        )
                        break

                    except asyncio.CancelledError:
                        raise

                    except Exception:
                        logger.exception(
                            f"Failed to process/commit message at "
                            f"offset={message.offset}. Retrying in "
                            f"{retry_delay} seconds without committing."
                        )
                        await asyncio.sleep(retry_delay)
                        retry_delay = min(retry_delay * 2, MAX_RETRY_DELAY_SECONDS)

        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Kafka consumer loop failed")
            raise

    
    @staticmethod
    def _deserialize_value(value: bytes) -> Dict[str, Any]:
        """Deserialize JSON value"""
        return json.loads(value.decode("utf-8"))