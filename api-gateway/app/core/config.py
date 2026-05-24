from pydantic_settings import BaseSettings


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
    
    # Rate Limiting
    RATE_LIMIT_REPLENISH_RATE: int = 10  # requests per minute
    RATE_LIMIT_BURST_CAPACITY: int = 20
    
    # Protected paths
    PROTECTED_PATHS: list = [
        "/api/transactions",
        "/api/rewards",
        "/api/notify"
    ]
    
    SECRET_KEY : str  
    ALGORITHM : str
    ACCESS_TOKEN_EXPIRE_MINUTES : int 
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()