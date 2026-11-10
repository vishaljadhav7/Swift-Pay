from pydantic_settings import BaseSettings


class Settings(BaseSettings):    
    # Service
    SERVICE_NAME: str = "notification-service"
    SERVICE_PORT: int = 8084   
    
    # JWT verification needs only the PUBLIC key. The private key stays in user-service.
    JWT_PUBLIC_KEY_PATH: str = "/keys/user-service.public.pem"
    JWT_ISSUER: str = "swiftpay-user-service"
    JWT_AUDIENCE: str = "swiftpay-api" 
    
    # Database
    DATABASE_URL: str 
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_TOPIC: str = "txn-initiated"   
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()