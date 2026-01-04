from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session dependency
    Yields an async database session and ensures proper cleanup
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()