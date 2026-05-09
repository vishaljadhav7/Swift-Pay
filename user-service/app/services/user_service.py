from sqlalchemy.ext.asyncio import AsyncSession
from typing import Tuple, List
import logging
from app.schemas.user import  LoginRequest,  UserResponse, WalletCreateRequest, SignupRequest
from app.models.user import User, Roles
from hyx.circuitbreaker import consecutive_breaker
from app.repositories.user import user_repository
from app.services.security_service import security_service
from app.core.exceptions import (
    InvalidCredentialsError,
    UserNotFoundException,
    ServiceUnavailableException
)
import httpx

logger = logging.getLogger(__name__)

class UserService:
    
    def __init__(self):
        self.wallet_service_url = "http://localhost:8088/api/v1/wallets"
        
        self.wallet_breaker = consecutive_breaker(
            failure_threshold=5,
            recovery_time_secs=30,
        )
        
        
    async def signup(self, db: AsyncSession, data: SignupRequest) -> str:
        """
        Register a new user and create wallet
        Returns success message with user ID
        """
        # Hash password
        hashed_password = security_service.hash_password(data.password)
        
        # Create user
        user = User(
            name=data.name,
            email=data.email,
            password=hashed_password,
            role=Roles.USER
        )
        
        created_user = await user_repository.create(db, user)
        
        try:
            await self._create_wallet_for_user(created_user.id)
        except Exception as e:
            # Rollback: delete user if wallet creation fails
            await user_repository.delete(db, created_user.id)
            raise ServiceUnavailableException("Wallet")
        
        return f"User registered successfully with ID: {created_user.id}"        
    
    async def login(self, db: AsyncSession, credentials: LoginRequest) -> Tuple[str, str]:
        
        user = await user_repository.get_by_email(db, credentials.email)
        if not user:
            raise InvalidCredentialsError()
        
        if not security_service.verify_password(credentials.password, user.password):
            raise InvalidCredentialsError()
        
        access_token, jti, expires_in = security_service.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role
        )
        
        return access_token, "bearer"
    
    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> UserResponse:
        """Get user by ID"""
        user = await user_repository.get_by_id(db, user_id)
        if not user:
            raise UserNotFoundException(user_id)
        return UserResponse.from_orm(user)
    
    async def get_all_users(self, db: AsyncSession) -> List[UserResponse]:
        """Get all users"""
        users = await user_repository.get_all(db)
        return [UserResponse.from_orm(user) for user in users]
    
    async def _create_wallet_for_user(self, user_id: str):
        async def create_wallet():
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.wallet_service_url,
                    json={"user_id": user_id, "currency": "INR"},
                    timeout=10.0
                )
                response.raise_for_status()

        try:
            async with self.wallet_breaker:
                await create_wallet()
        except Exception as e:
            logger.error(f"Wallet creation failed for user {user_id}: {e}")
            raise ServiceUnavailableException("Wallet")
    
    
user_service = UserService()