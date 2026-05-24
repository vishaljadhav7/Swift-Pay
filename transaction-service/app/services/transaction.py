from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import httpx    
import logging
from hyx.circuitbreaker import consecutive_breaker
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreateRequest, TransactionResponse
from app.repositories.transaction import transaction_repository

from app.core.exceptions import (
    TransactionNotFoundException,
    ServiceUnavailableException,
    DuplicateTransactionException
)

from app.utils.kafka_client import KafkaProducerClient

logger = logging.getLogger(__name__)


class TransactionService:
    """Handles transaction orchestration"""
    
    def __init__(self):
        self.wallet_service_url = "http://wallet-service:8088/api/v1/wallets"
        self.kafka_producer: KafkaProducerClient | None = None
        
        self.wallet_breaker = consecutive_breaker(
            failure_threshold=5,
            recovery_time_secs=30,
        )
    
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
        """
        # Check if transaction with this idempotency_key exists
        existing = await transaction_repository.get_by_idempotency_key(
            db, 
            data.idempotency_key
        )
        
        if existing:
            logger.warning(f"Duplicate transaction detected: {data.idempotency_key}")
            raise DuplicateTransactionException(data.idempotency_key)
                        
        logger.info("Entered create transaction")
        
        sender_id = data.sender_id
        receiver_id = data.receiver_id
        amount = data.amount
        
        transaction = Transaction(
            sender_id=sender_id,
            receiver_id=receiver_id,
            amount=amount,
            status="PENDING",
            idempotency_key=data.idempotency_key
        )
        
        saved_transaction = await transaction_repository.create(db, transaction)
        
        logger.info(f"Transaction PENDING saved: {saved_transaction.id}")
        
        hold_reference = None
        captured = False
        
        try:     
            # Place hold on sender wallet
            hold_reference = await self._place_hold(sender_id, amount)
            logger.info(f"Hold placed: {hold_reference}")
            
            # Check receiver wallet exists
            try:
                await self._check_wallet_exists(receiver_id)
            except Exception as e:
                logger.error(f"Receiver wallet missing: {e}")
                await self._release_hold(hold_reference)
                saved_transaction.status = "FAILED"
                await transaction_repository.update(db, saved_transaction)
                logger.info("Transaction FAILED (receiver wallet missing)")
                return TransactionResponse.from_orm(saved_transaction)
            
            # Capture hold → debit sender wallet
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
            
            # Credit receiver wallet
            try:
                await self._credit_wallet(receiver_id, amount)
                logger.info(" Receiver credited successfully")
            except Exception as e:
                logger.error(f"Credit failed: {e}")
                # Compensating transaction: refund sender
                try:
                    await self._credit_wallet(sender_id, amount)
                    logger.info("Compensating refund to sender succeeded")
                except Exception as refund_error:
                    logger.error(f"Compensating refund failed: {refund_error}")
                
                saved_transaction.status = "FAILED"
                await transaction_repository.update(db, saved_transaction)
                logger.info("Transaction FAILED (credit failed & refunded sender)")
                return TransactionResponse.from_orm(saved_transaction)
            
            # Mark transaction as SUCCESS
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
        
        # Send Kafka event
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
    
    async def _call_wallet_service(self, method: str, endpoint: str, json_data: dict = None):
        async def make_request():
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=f"{self.wallet_service_url}{endpoint}",
                    json=json_data,
                    timeout=10.0,
                )
                response.raise_for_status()
                body = response.text
                if not body.strip():
                    raise ValueError(
                        f"Empty response body from {endpoint} (status {response.status_code})"
                    )
                return response.json()
        try:
            async with self.wallet_breaker:
                return await make_request()
        except Exception as e:
            logger.error(f"Wallet service call failed [{endpoint}]: {e}")
            raise ServiceUnavailableException("Wallet")
        
    async def _place_hold(self, user_id: str, amount: int) -> str:
        result = await self._call_wallet_service(
            method="POST",
            endpoint="/hold",
            json_data={"user_id": user_id, "currency": "INR", "amount": int(amount)}
        )
        return result["hold_reference"]    
        
    
    async def _capture_hold(self, hold_reference: str):
        await self._call_wallet_service(
            method="POST",
            endpoint="/capture",
            json_data={"hold_reference": hold_reference}
        )
    
    async def _credit_wallet(self, user_id: str, amount: int):
        await self._call_wallet_service(
            method="POST",
            endpoint="/credit",
            json_data={"user_id": user_id, "currency": "INR", "amount": int(amount)}
        )

    async def _check_wallet_exists(self, user_id: str):
        await self._call_wallet_service(
            method="GET",
            endpoint=f"/{user_id}",
            json_data=None
        )
        
    async def _release_hold(self, hold_reference: str):
        try:
            await self._call_wallet_service(
                method="POST",
                endpoint=f"/release/{hold_reference}",
                json_data=None
            )
        except Exception as e:
            logger.error(f"Release hold failed (best-effort): {e}")        
        
transaction_service = TransactionService()