from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Service
    SERVICE_NAME: str = "api-gateway"
    SERVICE_PORT: int = 8080
    
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