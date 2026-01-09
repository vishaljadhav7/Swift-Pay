"""
Reward Kafka Consumer
Consumes transaction events and awards points
"""
import logging
from typing import Dict, Any
from datetime import datetime

from app.core.database import AsyncSessionLocal
from app.models.reward import Reward
from app.repositories.reward import reward_repository

logger = logging.getLogger(__name__)


class RewardConsumer:
    """Handles Kafka message consumption for rewards"""
    
    async def handle_transaction_event(self, event_data: Dict[str, Any]):
        """Process transaction event and award points"""
        try:
            transaction_id = event_data.get("id")
            sender_id = event_data.get("sender_id")
            amount = event_data.get("amount", 0)
            
            logger.info(f"Received transaction event: transaction_id={transaction_id}")
            
            async with AsyncSessionLocal() as db:
                # Idempotency check: ensure reward doesn't already exist
                exists = await reward_repository.exists_by_transaction_id(db, transaction_id)
                if exists:
                    logger.warning(f"⚠️ Reward already exists for transaction: {transaction_id}")
                    return
                
                # Calculate points: amount * 100
                points = amount * 100
                
                # Create reward
                reward = Reward(
                    user_id=sender_id,
                    points=points,
                    sent_at=datetime.utcnow(),
                    transaction_id=transaction_id
                )
                
                created_reward = await reward_repository.create(db, reward)
                logger.info(f"Reward saved: {created_reward.id}, points={points}")
        
        except Exception as e:
            logger.error(f"Failed to process transaction {transaction_id}: {e}", exc_info=True)
            raise


# Singleton instance
reward_consumer = RewardConsumer()