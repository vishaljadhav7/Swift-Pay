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

    # Deny by default: only these exact paths work without a token.
    # ("/docs" and "/openapi.json" are for development only; remove them in production.)
    PUBLIC_PATHS: list[str] = ["/", "/docs", "/openapi.json", "/auth/login", "/auth/signup"]

    # JWT: must match user-service. SECRET_KEY >= 43 characters
    SECRET_KEY: str = Field(min_length=43)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_ISSUER: str = "swiftpay-user-service"
    JWT_AUDIENCE: str = "swiftpay-api"

    # Browser origins allowed to call the API, e.g. ["http://localhost:3000"]
    CORS_ALLOWED_ORIGINS: list[str] = []
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()