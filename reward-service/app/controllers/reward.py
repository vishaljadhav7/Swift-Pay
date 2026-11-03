from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.auth import CurrentUser, get_current_user, ensure_owner_or_admin
from app.schemas.reward import RewardResponse
from app.services.reward import reward_service
from app.core.dependencies import get_db
from app.core.pagination import Page, DEFAULT_LIMIT, MAX_LIMIT


router = APIRouter(prefix="/api/v1/rewards", tags=["Reward"])


@router.get("/user/{user_id}", response_model=Page[RewardResponse])
async def get_rewards_by_user(
    user_id: str,
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    cursor: str | None = None,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Page[RewardResponse]:
    ensure_owner_or_admin(user, user_id)
    return await reward_service.get_rewards_by_user_id(db, user_id, limit, cursor)