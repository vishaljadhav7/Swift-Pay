from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.reward import RewardResponse
from app.services.reward import reward_service
from app.core.dependencies import get_db


router = APIRouter(prefix="/api/rewards", tags=["Reward"])


@router.get("", response_model=List[RewardResponse])
async def get_all_rewards(
    db: AsyncSession = Depends(get_db)
) -> List[RewardResponse]:
    """Get all rewards"""
    return await reward_service.get_all_rewards(db)


@router.get("/user/{user_id}", response_model=List[RewardResponse])
async def get_rewards_by_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> List[RewardResponse]:
    """Get all rewards for a user"""
    return await reward_service.get_rewards_by_user_id(db, user_id)