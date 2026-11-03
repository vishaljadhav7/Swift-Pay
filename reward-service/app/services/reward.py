from sqlalchemy.ext.asyncio import AsyncSession
from app.core.pagination import Page
from app.schemas.reward import RewardResponse
from app.repositories.reward import reward_repository

class RewardService:
    """Handles reward business logic"""
    
    async def get_rewards_by_user_id(self, db: AsyncSession, user_id: str, limit: int, cursor: str | None) -> Page[RewardResponse]:
        rewards, next_cursor = await reward_repository.get_by_user_id(db, user_id, limit, cursor)
        return Page(items=[RewardResponse.from_orm(r) for r in rewards], next_cursor=next_cursor)



reward_service = RewardService()