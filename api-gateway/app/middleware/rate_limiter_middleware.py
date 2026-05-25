from typing import Dict, Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """In-memory rate limiter"""
    
    def __init__(self, replenish_rate: int = 10, burst_capacity: int = 20):
        self.replenish_rate = replenish_rate  # requests per minute
        self.burst_capacity = burst_capacity
        self.buckets: Dict[str, Dict] = {}
        
        
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed"""
        now = datetime.utcnow()
        
        if key not in self.buckets:
            self.buckets[key] = {
                "tokens" : self.burst_capacity,
                "last_refill" : now
            }
            
        bucket = self.buckets[key]
        
        time_passed = (now - bucket["last_refill"]).total_seconds()   
        tokens_to_add = (time_passed / 60.0) * self.replenish_rate
        bucket["tokens"] = min(self.burst_capacity, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = now
        
        # Check if request is allowed
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True
        
        return False

class RateLimiterMiddleware(BaseHTTPMiddleware):
        
    """Rate limiter middleware"""
    
    def __init__(self, app, rate_limiter: RateLimiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter
        
    async def dispatch(self, request: Request, call_next: Callable):
        """Process the request with rate limiting"""
                
        user_id = request.headers.get("X-User-Id")
        key = user_id if user_id else request.client.host
        
        
        # Check rate limit
        if not self.rate_limiter.is_allowed(key):
            logger.warning(f"Rate limit exceeded for key: {key}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"}
            )
        return await call_next(request)
    
    
