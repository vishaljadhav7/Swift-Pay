from fastapi import APIRouter, Depends, Request, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.transaction import TransactionCreateRequest, TransactionResponse

from app.services.transaction import transaction_service
from app.core.dependencies import get_db
from app.core.exceptions import ForbiddenException
from app.core.auth import CurrentUser, get_current_user, ensure_owner_or_admin
from app.core.pagination import Page, DEFAULT_LIMIT, MAX_LIMIT

router = APIRouter(prefix="/api/v1/transactions", tags=["Transaction"])


@router.post("", response_model=TransactionResponse)
async def create_transaction(
    data: TransactionCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TransactionResponse:
    """Create a money transfer transaction (the sender must be the logged-in user)"""
    if data.sender_id != user.id:
        raise ForbiddenException(
            "User ID mismatch: You are not authorized to create this transaction"
        )
    return await transaction_service.create_transaction(db, data)


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction_by_id(
    transaction_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TransactionResponse:
    """Get transaction by ID (sender, receiver, or an admin)"""
    txn = await transaction_service.get_transaction_by_id(db, transaction_id)
    ensure_owner_or_admin(user, txn.sender_id, txn.receiver_id)
    return txn


@router.get("/user/{user_id}", response_model=Page[TransactionResponse])
async def get_transactions_by_user(
    user_id: str,
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    cursor: str | None = None,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Page[TransactionResponse]:
    ensure_owner_or_admin(user, user_id)
    return await transaction_service.get_transactions_by_user(db, user_id, limit, cursor)