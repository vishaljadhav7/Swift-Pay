from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from datetime import datetime
from app.models.wallet import Wallet, WalletHold
from app.core.exceptions import ConflictException, WalletNotFoundException, HoldNotFoundException



class WalletRepository:
    """Handling database operations for wallets"""
    
    async def create(self, db: AsyncSession, wallet: Wallet) -> Wallet:
        """Create a new wallet"""
        try:
            db.add(wallet)
            await db.commit()
            await db.refresh(wallet)
            return wallet
        except IntegrityError:
            await db.rollback()
            raise ConflictException(f"Wallet already exists for user {wallet.user_id}")
        
        
    async def update(self, db: AsyncSession, wallet: Wallet) -> Wallet:
        """Update wallet"""
        wallet.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(wallet)
        return wallet
    
    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> Optional[Wallet]:
        """Get wallet by user ID"""
        stmt = select(Wallet).where(Wallet.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    

    
    
wallet_repository = WalletRepository()    