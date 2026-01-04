from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from app.models.user import User
from app.core.exceptions import UserAlreadyExistsException


class UserRepository:
    """Handles database operations for users"""
    
    async def create(self, db: AsyncSession, user: User) -> User:
        """Create a new user"""
        try:
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user
        except IntegrityError:
            await db.rollback()
            raise UserAlreadyExistsException(user.email)
    
    async def get_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(self, db: AsyncSession) -> List[User]:
        """Get all users"""
        stmt = select(User)
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def delete(self, db: AsyncSession, user_id: int) -> bool:
        """Delete user by ID"""
        user = await self.get_by_id(db, user_id)
        if user:
            await db.delete(user)
            await db.commit()
            return True
        return False


# Singleton instance
user_repository = UserRepository()