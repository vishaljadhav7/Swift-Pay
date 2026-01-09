from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Optional, List
from app.models.transaction import Transaction


class TransactionRepository:
    """Handles database operations for transactions"""
    
    async def create(self, db: AsyncSession, transaction: Transaction) -> Transaction:
        """Create a new transaction"""
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        return transaction
    
    async def get_by_id(self, db: AsyncSession, transaction_id: str) -> Optional[Transaction]:
        """Get transaction by ID"""
        stmt = select(Transaction).where(Transaction.id == transaction_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_idempotency_key(self, db: AsyncSession, idempotency_key: str) -> Optional[Transaction]:
        """Get transaction by ID"""
        stmt = select(Transaction).where(Transaction.idempotency_key == idempotency_key)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_user(self, db: AsyncSession, user_id: str) -> List[Transaction]:
        """Get all transactions for a user (as sender or receiver)"""
        stmt = select(Transaction).where(
            or_(
                Transaction.sender_id == user_id,
                Transaction.receiver_id == user_id
            )
        ).order_by(Transaction.timestamp.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def update(self, db: AsyncSession, transaction: Transaction) -> Transaction:
        """Update transaction"""
        await db.commit()
        await db.refresh(transaction)
        return transaction
    
transaction_repository = TransactionRepository()    
    
    