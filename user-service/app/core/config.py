from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERVICE_NAME: str = "user-service"
    SERVICE_PORT: int = 8081
    
    DATABASE_URL: str
    
    WALLET_SERVICE_URL: str = "http://localhost:8088"
    
    SECRET_KEY : str  
    ALGORITHM : str
    ACCESS_TOKEN_EXPIRE_MINUTES : int 
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
        
settings = Settings()
