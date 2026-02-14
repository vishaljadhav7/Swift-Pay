from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import Optional, List
from app.models.transaction import Transaction
from app.core.exceptions import AppException


class TransactionRepository:
    """Handles database operations for transactions"""
    
    async def create(self, db: AsyncSession, transaction: Transaction) -> Transaction:
        """Create a new transaction"""
        try:
            db.add(transaction)
            await db.commit()
            await db.refresh(transaction)
            return transaction
        except IntegrityError as e:
            await db.rollback()
            raise AppException(f"Transaction creation failed: duplicate or constraint violation", status_code=409)
        except SQLAlchemyError as e:
            await db.rollback()
            raise AppException(f"Database error creating transaction: {str(e)}", status_code=500)
    
    async def get_by_id(self, db: AsyncSession, transaction_id: str) -> Optional[Transaction]:
        """Get transaction by ID"""
        try:
            stmt = select(Transaction).where(Transaction.id == transaction_id)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise AppException(f"Database error fetching transaction: {str(e)}", status_code=500)
    
    async def get_by_idempotency_key(self, db: AsyncSession, idempotency_key: str) -> Optional[Transaction]:
        """Get transaction by idempotency key"""
        try:
            stmt = select(Transaction).where(Transaction.idempotency_key == idempotency_key)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise AppException(f"Database error fetching transaction: {str(e)}", status_code=500)
    
    async def get_by_user(self, db: AsyncSession, user_id: str) -> List[Transaction]:
        """Get all transactions for a user (as sender or receiver)"""
        try:
            stmt = select(Transaction).where(
                or_(
                    Transaction.sender_id == user_id,
                    Transaction.receiver_id == user_id
                )
            ).order_by(Transaction.timestamp.desc())
            result = await db.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise AppException(f"Database error fetching user transactions: {str(e)}", status_code=500)
    
    async def update(self, db: AsyncSession, transaction: Transaction) -> Transaction:
        """Update transaction"""
        try:
            await db.commit()
            await db.refresh(transaction)
            return transaction
        except SQLAlchemyError as e:
            await db.rollback()
            raise AppException(f"Database error updating transaction: {str(e)}", status_code=500)
    
transaction_repository = TransactionRepository()