"""
Hold Expiry Scheduler
Background task to automatically release expired holds
"""
import asyncio
import logging
from app.core.database import AsyncSessionLocal
from app.services.wallet import wallet_service

logger = logging.getLogger(__name__)


class HoldExpiryScheduler:
    """Periodically checks and releases expired holds"""
    
    def __init__(self, scan_interval_seconds: int = 60):
        self.scan_interval_seconds = scan_interval_seconds
        self.running = False
        self.task = None
    
    async def start(self):
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        self.task = asyncio.create_task(self._run())
        logger.info(f"Hold expiry scheduler started (interval: {self.scan_interval_seconds}s)")
    
    async def stop(self):
        """Stop the scheduler"""
        if not self.running:
            return
        
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Hold expiry scheduler stopped")
    
    async def _run(self):
        """Main scheduler loop"""
        while self.running:
            try:
                await self._check_and_release_expired_holds()
            except Exception as e:
                logger.error(f"Error in hold expiry scheduler: {e}", exc_info=True)
            
            # Wait for next scan
            await asyncio.sleep(self.scan_interval_seconds)
    
    async def _check_and_release_expired_holds(self):
        """Check for and release expired holds"""
        async with AsyncSessionLocal() as db:
            try:
                count = await wallet_service.release_expired_holds(db)
                if count > 0:
                    logger.info(f"🔄 Released {count} expired hold(s)")
            except Exception as e:
                logger.error(f"Failed to release expired holds: {e}")


hold_expiry_scheduler = HoldExpiryScheduler(scan_interval_seconds=60)