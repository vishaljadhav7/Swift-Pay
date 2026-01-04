from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.wallet import (
    CreateWalletRequest,
    CreditRequest,
    DebitRequest,
    HoldRequest,
    CaptureRequest,
    WalletResponse,
    HoldResponse
)
from app.services.wallet import wallet_service
from app.core.dependencies import get_db

router = APIRouter(prefix="/api/v1/wallets", tags=["Wallet"])


@router.post("", response_model=WalletResponse, status_code=201)
async def create_wallet(
    request: CreateWalletRequest,
    db: AsyncSession = Depends(get_db)
) -> WalletResponse:
    """Create a new wallet"""
    return await wallet_service.create_wallet(db, request)

@router.get("/{user_id}", response_model=WalletResponse)
async def get_wallet(
    user_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db)
) -> WalletResponse:
    """Get wallet by user ID"""
    return await wallet_service.get_wallet(db, user_id)