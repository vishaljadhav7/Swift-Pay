from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, DBAPIError, SQLAlchemyError
from typing import Optional, List
from datetime import datetime
from app.models.wallet import Wallet, WalletHold, WalletStatuses
from app.core.exceptions import ConflictException, WalletNotFoundException, HoldNotFoundException, AppException

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
        except SQLAlchemyError as e:
            await db.rollback()
            raise AppException(f"Database error creating wallet: {str(e)}", status_code=500)
        
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
        try:
            stmt = (
                select(Wallet)
                .where(Wallet.user_id == user_id, Wallet.currency == currency)
                .with_for_update()  # Pessimistic locking
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise AppException(f"Database error fetching wallet: {str(e)}", status_code=500)
    
    async def update(self, db: AsyncSession, wallet: Wallet) -> Wallet:
        """Update wallet"""
        try:
            wallet.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(wallet)
            return wallet
        except SQLAlchemyError as e:
            await db.rollback()
            raise AppException(f"Database error updating wallet: {str(e)}", status_code=500)
    
    async def get_by_user_id(self, db: AsyncSession, user_id: str) -> Optional[Wallet]:
        """Get wallet by user ID"""
        try:
            stmt = select(Wallet).where(Wallet.user_id == user_id)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise AppException(f"Database error fetching wallet: {str(e)}", status_code=500)
    
    async def create_hold(self, db: AsyncSession, hold: WalletHold) -> WalletHold:
        """Create a wallet hold"""
        try:
            db.add(hold)
            await db.commit()
            await db.refresh(hold)
            return hold
        except IntegrityError:
            await db.rollback()
            raise ConflictException(f"Hold already exists with reference {hold.hold_reference}")
        except SQLAlchemyError as e:
            await db.rollback()
            raise AppException(f"Database error creating hold: {str(e)}", status_code=500)
    
    async def get_hold_by_reference(
        self, 
        db: AsyncSession, 
        hold_reference: str
    ) -> Optional[WalletHold]:
        """Get hold by reference"""
        try:
            stmt = (
                select(WalletHold)
                .where(WalletHold.hold_reference == hold_reference)
                .options(selectinload(WalletHold.wallet))
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise AppException(f"Database error fetching hold: {str(e)}", status_code=500)
    
    async def get_expired_holds(self, db: AsyncSession) -> List[WalletHold]:
        """Get all expired active holds"""
        try:
            now = datetime.utcnow()
            stmt = (
                select(WalletHold)
                .where(
                    WalletHold.status == WalletStatuses.ACTIVE,
                    WalletHold.expires_at <= now
                )
            )
            result = await db.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise AppException(f"Database error fetching expired holds: {str(e)}", status_code=500)
    
    async def update_hold(self, db: AsyncSession, hold: WalletHold) -> WalletHold:
        """Update hold"""
        try:
            await db.commit()
            await db.refresh(hold)
            return hold
        except SQLAlchemyError as e:
            await db.rollback()
            raise AppException(f"Database error updating hold: {str(e)}", status_code=500)
    

wallet_repository = WalletRepository()