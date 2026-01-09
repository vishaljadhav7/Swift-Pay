from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.transaction import TransactionCreateRequest, TransactionResponse

from app.services.transaction import transaction_service
from app.core.dependencies import get_db
from app.core.exceptions import ForbiddenException


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
    
    token_user_id = int(user_id_header)
    request_sender_id = data.sender_id
    
    # Verify authorization: user can only send from their own account
    if request_sender_id != token_user_id:
        raise ForbiddenException(
            "User ID mismatch: You are not authorized to create this transaction"
        )
    
    return await transaction_service.create_transaction(db, data)


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction_by_id(
    transaction_id: int,
    db: AsyncSession = Depends(get_db)
) -> TransactionResponse:
    """Get transaction by ID"""
    return await transaction_service.get_transaction_by_id(db, transaction_id)


@router.get("/user/{user_id}", response_model=List[TransactionResponse])
async def get_transactions_by_user(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> List[TransactionResponse]:
    """Get all transactions for a user"""
    # Read JWT userId forwarded by gateway
    token_user_id_header = request.headers.get("X-User-Id")
    if not token_user_id_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing X-User-Id header from gateway"
        )
    
    token_user_id = int(token_user_id_header)
    
    # Ensure user can only fetch their own transactions
    if user_id != token_user_id:
        raise ForbiddenException("You are not authorized to view these transactions")
    
    return await transaction_service.get_transactions_by_user(db, user_id)