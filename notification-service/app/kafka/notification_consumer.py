"""
Notification Kafka Consumer
Consumes transaction events and creates notifications
"""
import logging
from typing import Dict, Any
from datetime import datetime

from app.core.database import AsyncSessionLocal
from app.schemas.notification import NotificationCreate
from app.services.notification import notification_service

from app.repositories.notification import notification_repository
logger = logging.getLogger(__name__)


class NotificationConsumer:
    """Handles Kafka message consumption for notifications"""
    
    async def handle_transaction_event(self, event_data: Dict[str, Any]):
        """Process transaction event and create notification"""
        try:
            logger.info(f"Received transaction event: {event_data}")

            transaction_id = event_data.get("id")
            amount = event_data.get("amount", 0)
            sender_id = event_data.get("sender_id")
            receiver_id = event_data.get("receiver_id")

            message = f"{amount:.2f} received from user {sender_id}"

            async with AsyncSessionLocal() as db:
                # The same event can arrive twice (at-least-once delivery): skip if already handled
                if await notification_repository.exists_by_transaction_id(db, transaction_id):
                    logger.warning(f"Notification already exists for transaction: {transaction_id}")
                    return

                notification_data = NotificationCreate(
                    user_id=receiver_id,
                    message=message,
                    transaction_id=transaction_id,
                )
                notification = await notification_service.send_notification(db, notification_data)
                logger.info(f" Notification saved: {notification.id}")

        except Exception as e:
            logger.error(f"Failed to process transaction event: {e}", exc_info=True)
            raise


notification_consumer = NotificationConsumer()