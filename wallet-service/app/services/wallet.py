from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import secrets
from app.models.wallet import Wallet, WalletHold, WalletStatuses
from app.schemas.wallet import (
    CreateWalletRequest,
    CreditRequest,
    DebitRequest,
    HoldRequest,
    CaptureRequest,
    WalletResponse,
    HoldResponse
)
        
from app.repositories.wallet import wallet_repository

from app.core.exceptions import (
    InsufficientFundsException,
    WalletNotFoundException,
    HoldNotFoundException,
    BadRequestException
)
import logging

logger = logging.getLogger(__name__)


class WalletService:
    """Handles wallet business logic"""
    
    HOLD_EXPIRY_MINUTES = 10  # Holds expire after 10 minutes
    
    async def create_wallet(
        self, 
        db: AsyncSession, 
        data: CreateWalletRequest
    ) -> WalletResponse:
        """Create a new wallet"""
        wallet = Wallet(
            user_id=data.user_id,
            currency=data.currency,
            balance=500,
            available_balance=500
        )
        created = await wallet_repository.create(db, wallet)
        return WalletResponse.from_orm(created)
    
    
    async def credit(self, db: AsyncSession, data: CreditRequest) -> WalletResponse:
        """
        Credit money to wallet
        Increases both balance and available_balance
        """
        logger.info(f"CREDIT request: user_id={data.user_id}, amount={data.amount}")
        
        # Get wallet with lock
        wallet = await wallet_repository.get_by_user_id_with_lock(
            db, data.user_id, data.currency
        )
        if not wallet:
            raise WalletNotFoundException(data.user_id)
        
        # Update balances
        wallet.balance += data.amount
        wallet.available_balance += data.amount
        
        # Save wallet
        updated = await wallet_repository.update(db, wallet)
        
        logger.info(f"CREDIT done: wallet_id={wallet.id}, new_balance={wallet.balance}")
        return WalletResponse.from_orm(updated)
    
    async def debit(self, db: AsyncSession, data: DebitRequest) -> WalletResponse:
        """
        Debit money from wallet
        Decreases both balance and available_balance
        """
        logger.info(f" DEBIT request: user_id={data.user_id}, amount={data.amount}")
        
        # Get wallet with lock
        wallet = await wallet_repository.get_by_user_id_with_lock(
            db, data.user_id, data.currency
        )
        if not wallet:
            raise WalletNotFoundException(data.user_id)
        
        # Check sufficient funds
        if wallet.available_balance < data.amount:
            raise InsufficientFundsException("Not enough balance")
        
        # Update balances
        wallet.balance -= data.amount
        wallet.available_balance -= data.amount
        
        # Save wallet
        updated = await wallet_repository.update(db, wallet)
        
        logger.info(f" DEBIT done: wallet_id={wallet.id}, new_balance={wallet.balance}")
        return WalletResponse.from_orm(updated)
    
    async def get_wallet(self, db: AsyncSession, user_id: str) -> WalletResponse:
        """Get wallet by user ID"""
        wallet = await wallet_repository.get_by_user_id(db, user_id)
        if not wallet:
            raise WalletNotFoundException(user_id)
        return WalletResponse.from_orm(wallet)
    
    async def place_hold(self, db: AsyncSession, data: HoldRequest) -> HoldResponse:
        """
        Place a hold on wallet funds
        Reduces available_balance but not balance
        """
        logger.info(f"HOLD request: user_id={data.user_id}, amount={data.amount}")
        
        # Get wallet with lock
        wallet = await wallet_repository.get_by_user_id_with_lock(
            db, data.user_id, data.currency
        )
        if not wallet:
            raise WalletNotFoundException(data.user_id)
    
        
        # Check sufficient available funds
        if wallet.available_balance < data.amount:
            raise InsufficientFundsException("Not enough balance to hold")
        
        # Reduce available balance
        wallet.available_balance -= data.amount
        await wallet_repository.update(db, wallet)
        
        # Create hold
        hold_reference = f"HOLD-{int(datetime.utcnow().timestamp() * 1000)}-{secrets.token_hex(4)}"
        expires_at = datetime.utcnow() + timedelta(minutes=self.HOLD_EXPIRY_MINUTES)
        
        hold = WalletHold(
            hold_reference=hold_reference,
            amount=data.amount,
            status=WalletStatuses.ACTIVE,
            expires_at=expires_at
        )
        

        hold.wallet = wallet
        
        created_hold = await wallet_repository.create_hold(db, hold)
        
        logger.info(f"Hold placed: {hold_reference}, expires_at={expires_at}")
        return HoldResponse(
            hold_reference=created_hold.hold_reference,
            amount=created_hold.amount,
            status=created_hold.status
        )
    
    async def capture_hold(self, db: AsyncSession, data: CaptureRequest) -> WalletResponse:
        """
        Capture a hold - actually debit the money
        Reduces balance (available_balance already reduced during hold)
        """
        logger.info(f"CAPTURE request: hold_reference={data.hold_reference}")
        
        # Get hold
        hold = await wallet_repository.get_hold_by_reference(db, data.hold_reference)
        if not hold:
            raise HoldNotFoundException(data.hold_reference)
        
        if hold.status != WalletStatuses.ACTIVE:
            raise BadRequestException(f"Hold is not active (status: {hold.status})")
        
        # Get wallet with lock
        wallet = await wallet_repository.get_by_user_id_with_lock(
            db, hold.wallet.user_id, hold.wallet.currency
        )
        
        # Deduct from balance
        wallet.balance -= hold.amount
        await wallet_repository.update(db, wallet)
        
        # Mark hold as captured
        hold.status = WalletStatuses.CAPTURED
        await wallet_repository.update_hold(db, hold)
        
        logger.info(f"Hold captured: {data.hold_reference}")
        return WalletResponse.from_orm(wallet)
    
    async def release_hold(self, db: AsyncSession, hold_reference: str) -> HoldResponse:
        """
        Release a hold - restore available_balance
        """
        logger.info(f"RELEASE request: hold_reference={hold_reference}")
        
        # Get hold
        hold = await wallet_repository.get_hold_by_reference(db, hold_reference)
        if not hold:
            raise HoldNotFoundException(hold_reference)
        
        if hold.status != WalletStatuses.ACTIVE:
            raise BadRequestException(f"Hold is not active (status: {hold.status})")
        
        # Get wallet with lock
        wallet = await wallet_repository.get_by_user_id_with_lock(
            db, hold.wallet.user_id, hold.wallet.currency
        )
        
        # Restore available balance
        wallet.available_balance += hold.amount
        await wallet_repository.update(db, wallet)
        
        # Mark hold as released
        hold.status = WalletStatuses.RELEASED
        await wallet_repository.update_hold(db, hold)
        
        logger.info(f"Hold released: {hold_reference}")
        return HoldResponse(
            hold_reference=hold.hold_reference,
            amount=hold.amount,
            status=hold.status
        )
    
    async def release_expired_holds(self, db: AsyncSession) -> int:
        """
        Background task: Release expired holds
        Returns count of released holds
        """
        expired_holds = await wallet_repository.get_expired_holds(db)
        count = 0
        
        for hold in expired_holds:
            try:
                await self.release_hold(db, hold.hold_reference)
                count += 1
            except Exception as e:
                logger.error(f"Failed to release expired hold {hold.hold_reference}: {e}")
        
        return count
    
wallet_service = WalletService()    