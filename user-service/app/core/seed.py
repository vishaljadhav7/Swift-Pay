import logging

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.exceptions import UserAlreadyExistsException
from app.models.user import Roles, User
from app.repositories.user import user_repository
from app.services.security_service import security_service

logger = logging.getLogger(__name__)


async def seed_admin() -> None:
    """Create the first admin from ADMIN_EMAIL / ADMIN_PASSWORD. Safe to run on every startup."""
    if not (settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD):
        return
    async with AsyncSessionLocal() as db:
        if await user_repository.get_by_email(db, settings.ADMIN_EMAIL):
            return
        admin = User(
            name="Admin",
            email=settings.ADMIN_EMAIL,
            password=security_service.hash_password(settings.ADMIN_PASSWORD),
            role=Roles.ADMIN,
        )
        try:
            await user_repository.create(db, admin)
            logger.info("Admin user created")
        except UserAlreadyExistsException:
            pass  # another instance created it first