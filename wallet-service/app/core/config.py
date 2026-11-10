from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Service
    SERVICE_NAME: str = "wallet-service"
    SERVICE_PORT: int = 8088
    
    
    # JWT verification needs only the PUBLIC key. The private key stays in user-service.
    JWT_PUBLIC_KEY_PATH: str = "/keys/user-service.public.pem"
    JWT_ISSUER: str = "swiftpay-user-service"
    JWT_AUDIENCE: str = "swiftpay-api"

    TRANSACTION_SERVICE_PUBLIC_KEY_PATH: str = "/keys/transaction-service.public.pem"
    
    # Database
    DATABASE_URL: str 
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()