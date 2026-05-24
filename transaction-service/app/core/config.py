from pydantic_settings import BaseSettings


class Settings(BaseSettings):    
    # Service
    SERVICE_NAME: str = "transaction-service"
    SERVICE_PORT: int = 8082
    
    # Database
    DATABASE_URL: str 
    
    # Wallet Service
    WALLET_SERVICE_URL: str = "http://wallet-service:8088"
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_TOPIC: str = "txn-initiated"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()