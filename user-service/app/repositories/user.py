from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import Optional, List
from app.models.user import User
from app.core.exceptions import UserAlreadyExistsException, AppException


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
        except SQLAlchemyError as e:
            await db.rollback()
            raise AppException(f"Database error creating user: {str(e)}", status_code=500)
    
    async def get_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            stmt = select(User).where(User.id == user_id)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise AppException(f"Database error fetching user: {str(e)}", status_code=500)
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            stmt = select(User).where(User.email == email)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise AppException(f"Database error fetching user: {str(e)}", status_code=500)
    
    async def get_all(self, db: AsyncSession) -> List[User]:
        """Get all users"""
        try:
            stmt = select(User)
            result = await db.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise AppException(f"Database error fetching users: {str(e)}", status_code=500)
    
    async def delete(self, db: AsyncSession, user_id: int) -> bool:
        """Delete user by ID"""
        try:
            user = await self.get_by_id(db, user_id)
            if user:
                await db.delete(user)
                await db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            await db.rollback()
            raise AppException(f"Database error deleting user: {str(e)}", status_code=500)

user_repository = UserRepository()