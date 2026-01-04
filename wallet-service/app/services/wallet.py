from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import secrets
from app.models.wallet import Wallet, WalletHold
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
            balance=0,
            available_balance=0
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
    
    async def get_wallet(self, db: AsyncSession, user_id: int) -> WalletResponse:
        """Get wallet by user ID"""
        wallet = await wallet_repository.get_by_user_id(db, user_id)
        if not wallet:
            raise WalletNotFoundException(user_id)
        return WalletResponse.from_orm(wallet)
    

wallet_service = WalletService()    