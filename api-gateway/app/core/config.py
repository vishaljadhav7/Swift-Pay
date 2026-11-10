from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings"""
    
    # Service
    SERVICE_NAME: str = "api-gateway"
    SERVICE_PORT: int = 8080
    
    
    USER_SERVICE_URL: str        = "http://user-service:8001"
    WALLET_SERVICE_URL: str      = "http://wallet-service:8088"
    TRANSACTION_SERVICE_URL: str = "http://transaction-service:8002"
    NOTIFICATION_SERVICE_URL: str= "http://notification-service:8003"
    REWARD_SERVICE_URL: str      = "http://reward-service:8004"
    
    # Rate limiting (per verified user id, or per client IP when not logged in)
    RATE_LIMIT_REPLENISH_RATE: int = 10  # requests per minute
    RATE_LIMIT_BURST_CAPACITY: int = 20


    # Browser origins allowed to call the API, e.g. ["http://localhost:3000"]
    CORS_ALLOWED_ORIGINS: list[str] = []
    

settings = Settings()