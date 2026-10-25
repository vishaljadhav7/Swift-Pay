from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    SERVICE_NAME: str = "user-service"
    SERVICE_PORT: int = 8081
    
    DATABASE_URL: str 
    
    WALLET_SERVICE_URL: str = "http://wallet-service:8088"
    
    SECRET_KEY : str  = Field(min_length=43)
    ALGORITHM : str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES : int 
    
    JWT_ISSUER: str = "swiftpay-user-service"
    JWT_AUDIENCE: str = "swiftpay-api"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
        
settings = Settings()
