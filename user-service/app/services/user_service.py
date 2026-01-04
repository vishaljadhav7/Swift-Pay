from sqlalchemy.ext.asyncio import AsyncSession
from typing import Tuple, List
from app.schemas.user import  LoginRequest,  UserResponse
from app.repositories.user import user_repository

from app.services.security_service import security_service
from app.core.exceptions import (
    InvalidCredentialsError,
    UserNotFoundException,
    ServiceUnavailableException
)


class UserService:
    
    def __init__(self):
        self.wallet_service_url = ""
    
    
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
    
    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> UserResponse:
        """Get user by ID"""
        user = await user_repository.get_by_id(db, user_id)
        if not user:
            raise UserNotFoundException(user_id)
        return UserResponse.from_orm(user)
    
    async def get_all_users(self, db: AsyncSession) -> List[UserResponse]:
        """Get all users"""
        users = await user_repository.get_all(db)
        return [UserResponse.from_orm(user) for user in users]
    
    

# Singleton instance
user_service = UserService()