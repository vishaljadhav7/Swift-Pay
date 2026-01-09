from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.reward import RewardResponse
from app.repositories.reward import reward_repository

class RewardService:
    """Handles reward business logic"""
    
    async def get_all_rewards(self, db: AsyncSession) -> List[RewardResponse]:
        """Get all rewards"""
        rewards = await reward_repository.get_all(db)
        return [RewardResponse.from_orm(r) for r in rewards]
    
    async def get_rewards_by_user_id(
        self, 
        db: AsyncSession, 
        user_id: str
    ) -> List[RewardResponse]:
        """Get all rewards for a user"""
        rewards = await reward_repository.get_by_user_id(db, user_id)
        return [RewardResponse.from_orm(r) for r in rewards]



reward_service = RewardService()