import asyncio 
import logging
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.outbox_event import OutboxEvent

logger = logging.getLogger(__name__)

POLL_SECONDS = 10

async def publish_next(producer) -> bool:
    """Send the oldest unsent event to Kafka and mark it sent. Returns False when nothing is left."""
    
    async with AsyncSessionLocal() as db:
        event = (await db.scalars(
            select(OutboxEvent)
            .where(OutboxEvent.published_at.is_(None))
            .order_by(OutboxEvent.created_at, OutboxEvent.id)
            .limit(1)
            .with_for_update(skip_locked=True)
        )).first()
        
        if event is None:
            return False
        
        await producer.send_message(topic=event.topic, key=event.key, value=event.payload)
        event.published_at = datetime.now(timezone.utc)
        await db.commit()
        return True
    
async def run_outbox_relay(producer):
        """Background loop: keep sending unsent events. If Kafka is down, rows wait and are retried."""
        
        while True:
            try:
                while await publish_next(producer):
                    pass
            except Exception as e:
                logger.error(f"Outbox relay failed, will retry: {e}")
                
            await asyncio.sleep(POLL_SECONDS)    
            
        