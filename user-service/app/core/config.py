from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    SERVICE_NAME: str = "user-service"
    SERVICE_PORT: int = 8081
    
    DATABASE_URL: str 
    
    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None
    
    WALLET_SERVICE_URL: str = "http://wallet-service:8088"
    
    # JWT keys: user-service signs with the private key; every service verifies with the public key
    PRIVATE_KEY_PATH: str = "/keys/user-service.private.pem"
    JWT_PUBLIC_KEY_PATH: str = "/keys/user-service.public.pem"
    
    ACCESS_TOKEN_EXPIRE_MINUTES : int 
    
    JWT_ISSUER: str = "swiftpay-user-service"
    JWT_AUDIENCE: str = "swiftpay-api"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
        
settings = Settings()
