from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.transaction import TransactionCreateRequest, TransactionResponse

from app.services.transaction import transaction_service
from app.core.dependencies import get_db
from app.core.exceptions import ForbiddenException
from app.core.auth import CurrentUser, get_current_user, ensure_owner_or_admin

router = APIRouter(prefix="/api/transactions", tags=["Transaction"])



@router.post("/create", response_model=TransactionResponse)
async def create_transaction(
    request: Request,
    data: TransactionCreateRequest,
    db: AsyncSession = Depends(get_db)
) -> TransactionResponse:
    """Create a money transfer transaction"""
    # Read userId from gateway header
    user_id_header = request.headers.get("X-User-Id")
    
    if not user_id_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing X-User-Id header from gateway"
        )
    
    token_user_id = str(user_id_header)
    request_sender_id = data.sender_id
    
    # Verify authorization: user can only send from their own account
    if request_sender_id != token_user_id:
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


@router.get("/user/{user_id}", response_model=List[TransactionResponse])
async def get_transactions_by_user(
    user_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[TransactionResponse]:
    """Get all transactions for a user (the user themselves, or an admin)"""
    ensure_owner_or_admin(user, user_id)
    return await transaction_service.get_transactions_by_user(db, user_id)