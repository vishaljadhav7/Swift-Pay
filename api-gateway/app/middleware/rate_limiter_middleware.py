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
    
    
    
    
#     Your FastAPI gateway implementation is a solid start for a microservices architecture. You've correctly implemented a **Token Bucket** algorithm for rate limiting and structured your middleware stack logically.

# However, there are a few critical areas—specifically around **concurrency, scalability, and security**—that you should address before moving this to production.

# ---

# ## 1. The Concurrency Issue (Race Conditions)
# In your `is_allowed` method, you are performing a "read-modify-write" operation on the `self.buckets` dictionary. 

# Since FastAPI handles requests concurrently using `anyio` threads or an event loop, two requests from the same user arriving at the exact same millisecond could both read `tokens = 1`, both subtract `1`, and both proceed, even if only one token was available.

# **Solution:** Use an `asyncio.Lock` if this remains in-memory, or move to an atomic Redis operation.

# ---

# ## 2. In-Memory vs. Distributed Storage
# Currently, your `RateLimiter` stores data in `self.buckets`. 
# * **The Problem:** If you run multiple workers (e.g., `uvicorn --workers 4`) or scale to multiple Docker containers, each instance will have its own private bucket. A user could bypass your limit by hitting different instances.
# * **The Fix:** Use **Redis** for the bucket storage. Redis's `INCR` and `EXPIRE` commands (or a Lua script) allow for atomic, distributed rate limiting across all gateway instances.

# ---

# ## 3. Middleware Ordering
# In your `app.main`, you have:
# 1.  `RateLimiterMiddleware`
# 2.  `AuthMiddleware`

# **The Logic:** This means you are rate-limiting users *before* you authenticate them.
# * **Pros:** Protects your auth logic (and database/identity provider) from being hammered.
# * **Cons:** Since `user_id` is extracted from headers in the middleware, an unauthenticated attacker can spoof `X-User-Id` to "frame" another user and get them rate-limited (a Denial of Service attack).
# * **Recommendation:** Move `AuthMiddleware` **above** `RateLimiterMiddleware` so you can rate-limit based on a verified, trusted `user_id`.

# ---

# ## 4. Code Improvements & Bug Fixes

# ### Use `now.timestamp()`
# Using `(now - last_refill).total_seconds()` is fine, but calculating with floating-point math for tokens can sometimes lead to precision issues. Storing the timestamp as a float (`time.time()`) is generally cleaner for these calculations.

# ### Header Leakage
# In your proxy route:
# ```python
# return await proxy_service.proxy_request(request)
# ```
# Ensure your `proxy_service` filters out hop-by-hop headers (like `Host`, `Content-Length`, `Transfer-Encoding`) before forwarding the request to the microservice, or the backend may reject the request.

# ### Refined `is_allowed` Logic (Atomic-style)
# If you stick with in-memory for now, here is a cleaner way to handle the update:

# ```python
# import time
# from threading import Lock

# class RateLimiter:
#     def __init__(self, replenish_rate: int, burst_capacity: int):
#         self.replenish_rate = replenish_rate 
#         self.burst_capacity = burst_capacity
#         self.buckets: Dict[str, Dict] = {}
#         self.lock = Lock() # Simple thread lock for safety

#     def is_allowed(self, key: str) -> bool:
#         with self.lock:
#             now = time.time()
#             if key not in self.buckets:
#                 self.buckets[key] = {"tokens": float(self.burst_capacity), "last_refill": now}

#             bucket = self.buckets[key]
            
#             # Calculate refill
#             passed = now - bucket["last_refill"]
#             # replenish_rate is per minute, so divide by 60 for per-second rate
#             refill_amount = passed * (self.replenish_rate / 60.0)
            
#             bucket["tokens"] = min(float(self.burst_capacity), bucket["tokens"] + refill_amount)
#             bucket["last_refill"] = now

#             if bucket["tokens"] >= 1.0:
#                 bucket["tokens"] -= 1.0
#                 return True
#             return False
# ```

# ---

# ## 5. Security Note: `X-User-Id`
# Relying on `request.headers.get("X-User-Id")` inside the middleware is dangerous if your Gateway is exposed directly to the internet. An external attacker could set this header themselves. 

# > **Best Practice:** Your `AuthMiddleware` should validate a JWT, and only *after* validation should it attach the `user_id` to the `request.state` (e.g., `request.state.user_id = decoded_token['sub']`). Your Rate Limiter should then pull from `request.state.user_id`.

# How are you currently handling the JWT validation inside that `AuthMiddleware`?