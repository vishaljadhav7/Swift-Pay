from pydantic_settings import BaseSettings


class Settings(BaseSettings):    
    # Service
    SERVICE_NAME: str = "reward-service"
    SERVICE_PORT: int = 8089
    
    # Database
    DATABASE_URL: str 
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_TOPIC: str = "txn-initiated"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()