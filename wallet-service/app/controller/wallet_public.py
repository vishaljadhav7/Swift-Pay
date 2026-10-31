from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.wallet import WalletResponse
from app.services.wallet import wallet_service
from app.core.dependencies import get_db
from app.core.auth import CurrentUser, get_current_user, ensure_owner_or_admin

router = APIRouter(prefix="/api/wallets", tags=["Wallet (public)"])


@router.get("/{user_id}", response_model=WalletResponse)
async def get_wallet_for_user(
    user_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> WalletResponse:
    """Get a wallet balance (the user themselves, or an admin)"""
    ensure_owner_or_admin(user, user_id)
    return await wallet_service.get_wallet(db, user_id)