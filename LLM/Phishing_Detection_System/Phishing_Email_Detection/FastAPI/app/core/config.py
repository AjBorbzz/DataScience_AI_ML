from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
import secrets

class Settings(BaseSettings):
    PROJECT_NAME: str = "Phishing Email Detection API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    DATABASE_URL: str = "sqlite:///./phishing_detection.db"
    
    # ML Model Settings
    MODEL_PATH: str = "ml_models/phishing_classifier.pkl"
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # Redis (for caching)
    REDIS_URL: Optional[str] = None
    
    # Email processing
    MAX_EMAIL_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EMAIL_TYPES: List[str] = ["text/plain", "text/html", "message/rfc822"]
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()