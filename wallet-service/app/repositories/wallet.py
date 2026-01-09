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
        
    async def get_by_user_id_with_lock(
        self, 
        db: AsyncSession, 
        user_id: str, 
        currency: str
    ) -> Optional[Wallet]:
        """
        Get wallet by user ID with pessimistic write lock
        Used for concurrent transaction safety
        """
        stmt = (
            select(Wallet)
            .where(Wallet.user_id == user_id, Wallet.currency == currency)
            .with_for_update()  # Pessimistic locking
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()        
    
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
    
    async def create_hold(self, db: AsyncSession, hold: WalletHold) -> WalletHold:
        """Create a wallet hold"""
        db.add(hold)
        await db.commit()
        await db.refresh(hold)
        return hold
    
    async def get_hold_by_reference(
        self, 
        db: AsyncSession, 
        hold_reference: str
    ) -> Optional[WalletHold]:
        """Get hold by reference"""
        stmt = select(WalletHold).where(WalletHold.hold_reference == hold_reference)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    
    async def get_expired_holds(self, db: AsyncSession) -> List[WalletHold]:
        """Get all expired active holds"""
        now = datetime.utcnow()
        stmt = (
            select(WalletHold)
            .where(
                WalletHold.status == "ACTIVE",
                WalletHold.expires_at <= now
            )
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    
    async def update_hold(self, db: AsyncSession, hold: WalletHold) -> WalletHold:
        """Update hold"""
        await db.commit()
        await db.refresh(hold)
        return hold
    
    
wallet_repository = WalletRepository()    