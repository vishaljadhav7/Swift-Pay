from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.user import (
    SignupRequest,
    LoginRequest,
    TokenResponse,
    UserResponse
)
from app.services.user_service import user_service
from app.core.dependencies import get_db

router = APIRouter()


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Login and get JWT token"""
    access_token, token_type = await user_service.login(db, request)
    return TokenResponse(access_token=access_token, token_type=token_type)


@router.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Get user by ID"""
    return await user_service.get_user_by_id(db, user_id)