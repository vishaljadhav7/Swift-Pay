from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Service
    SERVICE_NAME: str = "wallet-service"
    SERVICE_PORT: int = 8088
    
    # Database
    DATABASE_URL: str 
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()