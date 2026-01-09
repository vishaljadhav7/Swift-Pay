from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime
import httpx
import logging

from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreateRequest, TransactionResponse
from app.repositories.transaction import transaction_repository

from app.core.exceptions import (
    TransactionNotFoundException,
    ForbiddenException,
    BadRequestException,
    ServiceUnavailableException
)

from app.utils.kafka_client import KafkaProducerClient

logger = logging.getLogger(__name__)


class TransactionService:
    """Handles transaction orchestration"""
    
    def __init__(self):
        self.wallet_service_url = "http://localhost:8088/api/v1/wallets"
        self.kafka_producer: KafkaProducerClient | None = None
    
    def set_kafka_producer(self, producer: KafkaProducerClient):
        """Set Kafka producer instance"""
        self.kafka_producer = producer
        
    async def create_transaction(
        self, 
        db: AsyncSession, 
        data: TransactionCreateRequest
    ) -> TransactionResponse:
        
        """
        Create a money transfer transaction
        Implements 2-phase commit: Hold → Capture → Credit
        """
        # Check if transaction with this idempotency_key exists
        existing = await transaction_repository.get_by_idempotency_key(
            db, 
            data.idempotency_key
        )
        
        if existing:
            logger.info(f"Duplicate transaction detected: {data.idempotency_key}")
            return TransactionResponse.from_orm(existing)
                
        logger.info("Entered create transaction")
        
        sender_id = data.sender_id
        receiver_id = data.receiver_id
        amount = data.amount
        
        amount_in_paise = int(amount * 100)
        
        transaction = Transaction(
            sender_id=sender_id,
            receiver_id=receiver_id,
            amount=amount,
            status="PENDING"
        )
        
        saved_transaction = await transaction_repository.create(db, transaction)
        
        logger.info(f"Transaction PENDING saved: {saved_transaction.id}")
        
        hold_reference = None
        captured = False
        
        
        try:
            # Step 1: Place hold on sender wallet
            hold_reference = await self._place_hold(sender_id, amount_in_paise)
            logger.info(f"Hold placed: {hold_reference}")
            
            # Step 2: Check receiver wallet exists
            try:
                await self._check_wallet_exists(receiver_id)
            except Exception as e:
                logger.error(f"Receiver wallet missing: {e}")
                await self._release_hold(hold_reference)
                saved_transaction.status = "FAILED"
                await transaction_repository.update(db, saved_transaction)
                logger.info("Transaction FAILED (receiver wallet missing)")
                return TransactionResponse.from_orm(saved_transaction)
            
             # Step 3: Capture hold → debit sender wallet
            try:
                await self._capture_hold(hold_reference)
                captured = True
                logger.info("Hold captured → sender debited")
            except Exception as e:
                logger.error(f"Capture failed: {e}")
                await self._release_hold(hold_reference)
                saved_transaction.status = "FAILED"
                await transaction_repository.update(db, saved_transaction)
                logger.info("Transaction FAILED (capture failed)")
                return TransactionResponse.from_orm(saved_transaction)
            
            # Step 4: Credit receiver wallet
            try:
                await self._credit_wallet(receiver_id, amount_in_paise)
                logger.info("💰 Receiver credited successfully")
            except Exception as e:
                logger.error(f"Credit failed: {e}")
                # Compensating transaction: refund sender
                try:
                    await self._credit_wallet(sender_id, amount_in_paise)
                    logger.info("Compensating refund to sender succeeded")
                except Exception as refund_error:
                    logger.error(f"Compensating refund failed: {refund_error}")
                
                saved_transaction.status = "FAILED"
                await transaction_repository.update(db, saved_transaction)
                logger.info("Transaction FAILED (credit failed & refunded sender)")
                return TransactionResponse.from_orm(saved_transaction)
            
            # Step 5: Mark transaction as SUCCESS
            saved_transaction.status = "SUCCESS"
            await transaction_repository.update(db, saved_transaction)
            logger.info(f"Transaction SUCCESS: {saved_transaction.id}")
            
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            if hold_reference and not captured:
                await self._release_hold(hold_reference)
            saved_transaction.status = "FAILED"
            await transaction_repository.update(db, saved_transaction)
            logger.info("Transaction FAILED saved")
            return TransactionResponse.from_orm(saved_transaction)   
        
        
        # Step 6: Send Kafka event
        if self.kafka_producer and saved_transaction.status == "SUCCESS":
            try:
                event_data = {
                    "id": saved_transaction.id,
                    "sender_id": saved_transaction.sender_id,
                    "receiver_id": saved_transaction.receiver_id,
                    "amount": saved_transaction.amount,
                    "timestamp": saved_transaction.timestamp.isoformat(),
                    "status": saved_transaction.status
                }
                await self.kafka_producer.send_message(
                    topic="txn-initiated",
                    key=str(saved_transaction.id),
                    value=event_data
                )
                logger.info("Kafka message sent")
            except Exception as e:
                logger.error(f"Failed to send Kafka event: {e}")
        
        return TransactionResponse.from_orm(saved_transaction) 
        
        
    async def get_transaction_by_id(
        self, 
        db: AsyncSession, 
        transaction_id: int
    ) -> TransactionResponse:
        """Get transaction by ID"""
        transaction = await transaction_repository.get_by_id(db, transaction_id)
        if not transaction:
            raise TransactionNotFoundException(transaction_id)
        return TransactionResponse.from_orm(transaction)
    
    async def get_transactions_by_user(
        self, 
        db: AsyncSession, 
        user_id: int
    ) -> List[TransactionResponse]:
        """Get all transactions for a user"""
        transactions = await transaction_repository.get_by_user(db, user_id)
        return [TransactionResponse.from_orm(t) for t in transactions]
    
    # methods for wallet service calls
    
    async def _place_hold(self, user_id: int, amount: int) -> str:
        """Place hold on sender wallet"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.wallet_service_url}/hold",
                json={"user_id": user_id, "currency": "INR", "amount": amount},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            return data["hold_reference"]
    
    async def _capture_hold(self, hold_reference: str):
        """Capture hold (debit)"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.wallet_service_url}/capture",
                json={"hold_reference": hold_reference},
                timeout=10.0
            )
            response.raise_for_status()
    
    async def _release_hold(self, hold_reference: str):
        """Release hold"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.wallet_service_url}/release/{hold_reference}",
                    timeout=10.0
                )
                logger.info(f"Release response: status={response.status_code}")
        except Exception as e:
            logger.error(f"Failed to release hold [{hold_reference}]: {e}")
    
    async def _credit_wallet(self, user_id: int, amount: int):
        """Credit wallet"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.wallet_service_url}/credit",
                json={"user_id": user_id, "currency": "INR", "amount": amount},
                timeout=10.0
            )
            response.raise_for_status()
    
    async def _check_wallet_exists(self, user_id: int):
        """Check if wallet exists"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.wallet_service_url}/{user_id}",
                timeout=10.0
            )
            response.raise_for_status()    
        
transaction_service = TransactionService()        