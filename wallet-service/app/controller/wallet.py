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


@router.post("/credit", response_model=WalletResponse)
async def credit_wallet(
    request: CreditRequest,
    db: AsyncSession = Depends(get_db)
) -> WalletResponse:
    """Credit money to wallet"""
    return await wallet_service.credit(db, request)


@router.post("/debit", response_model=WalletResponse)
async def debit_wallet(
    request: DebitRequest,
    db: AsyncSession = Depends(get_db)
) -> WalletResponse:
    """Debit money from wallet"""
    return await wallet_service.debit(db, request)

@router.get("/{user_id}", response_model=WalletResponse)
async def get_wallet(
    user_id: str = Path(..., min_length=10),
    db: AsyncSession = Depends(get_db)
) -> WalletResponse:
    """Get wallet by user ID"""

    return await wallet_service.get_wallet(db, user_id)


@router.post("/hold", response_model=HoldResponse)
async def place_hold(
    request: HoldRequest,
    db: AsyncSession = Depends(get_db)
) -> HoldResponse:
    """Place a hold on wallet funds"""
    return await wallet_service.place_hold(db, request)


@router.post("/capture", response_model=WalletResponse)
async def capture_hold(
    request: CaptureRequest,
    db: AsyncSession = Depends(get_db)
) -> WalletResponse:
    """Capture a hold (actual debit)"""
    return await wallet_service.capture_hold(db, request)


@router.post("/release/{hold_reference}", response_model=HoldResponse)
async def release_hold(
    hold_reference: str = Path(..., min_length=1),
    db: AsyncSession = Depends(get_db)
) -> HoldResponse:
    """Release a hold"""
    return await wallet_service.release_hold(db, hold_reference)