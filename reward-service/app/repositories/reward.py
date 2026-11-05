from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.reward import Reward
from app.core.pagination import paginate

class RewardRepository:
    """Handles database operations for rewards"""
    
    async def create(self, db: AsyncSession, reward: Reward) -> Reward:
        """Create a new reward"""
        db.add(reward)
        await db.commit()
        await db.refresh(reward)
        return reward
    
    async def get_by_user_id(self, db: AsyncSession, user_id: str, limit: int, cursor: str | None):
        stmt = select(Reward).where(Reward.user_id == user_id)
        return await paginate(db, stmt, Reward.sent_at, Reward.id, limit, cursor)
    
    async def exists_by_transaction_id(self, db: AsyncSession, transaction_id: int) -> bool:
        """Check if reward already exists for transaction (idempotency)"""
        stmt = select(Reward).where(Reward.transaction_id == transaction_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None


reward_repository = RewardRepository()
