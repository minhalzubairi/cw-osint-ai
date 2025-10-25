"""
Configuration management for OSInt-AI
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "OSInt-AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # DigitalOcean
    DO_API_TOKEN: str = ""
    GRADIENT_AI_ENDPOINT: str = ""
    GRADIENT_AI_API_KEY: str = ""
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/osint_ai"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Data Sources
    GITHUB_TOKEN: str = ""
    NEWS_API_KEY: str = ""
    RSS_UPDATE_INTERVAL: int = 600
    
    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Data Collection
    MAX_REPOSITORIES_PER_USER: int = 100
    MAX_RSS_FEEDS_PER_USER: int = 50
    COLLECTION_INTERVAL: int = 300
    
    # AI Configuration
    AI_MODEL: str = "meta-llama/Llama-3.1-70B-Instruct"
    AI_MAX_TOKENS: int = 2048
    AI_TEMPERATURE: float = 0.7
    ANALYSIS_BATCH_SIZE: int = 10
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
