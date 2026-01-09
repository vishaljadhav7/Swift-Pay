from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.reward import Reward

class RewardRepository:
    """Handles database operations for rewards"""
    
    async def create(self, db: AsyncSession, reward: Reward) -> Reward:
        """Create a new reward"""
        db.add(reward)
        await db.commit()
        await db.refresh(reward)
        return reward
    
    async def get_by_user_id(self, db: AsyncSession, user_id: str) -> List[Reward]:
        """Get all rewards for a user"""
        stmt = select(Reward).where(
            Reward.user_id == user_id
        ).order_by(Reward.sent_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_all(self, db: AsyncSession) -> List[Reward]:
        """Get all rewards"""
        stmt = select(Reward).order_by(Reward.sent_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def exists_by_transaction_id(self, db: AsyncSession, transaction_id: int) -> bool:
        """Check if reward already exists for transaction (idempotency)"""
        stmt = select(Reward).where(Reward.transaction_id == transaction_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None


reward_repository = RewardRepository()
