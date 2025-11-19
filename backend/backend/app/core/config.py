from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # App Configuration
    APP_NAME: str = "Fundraising Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database Configuration
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    
    # JWT Configuration
    SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Admin account (predefined credentials)
    ADMIN_EMAIL: Optional[str] = None
    ADMIN_PASSWORD_HASH: Optional[str] = None  # bcrypt hash (use get_password_hash)
    
    # Payment Gateway Configuration
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    PAYPAL_CLIENT_ID: Optional[str] = None
    PAYPAL_CLIENT_SECRET: Optional[str] = None
    SQUARE_APPLICATION_ID: Optional[str] = None
    SQUARE_ACCESS_TOKEN: Optional[str] = None
    
    # Email Configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None  # Add this field to handle the extra input
    
    # URLs
    FRONTEND_URL: str = "https://srv1133545.hstgr.cloud"
    BACKEND_URL: str = "https://srv1133545.hstgr.cloud"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://srv1133545.hstgr.cloud",
        "http://srv1133545.hstgr.cloud",
        "https://72.61.174.202",
        "http://72.61.174.202",
    ]
    
    # Campaign Configuration
    MIN_CAMPAIGN_DURATION_MONTHS: int = 1
    MAX_CAMPAIGN_DURATION_MONTHS: int = 12
    CAMPAIGN_MONTHLY_COST: float = 10.0
    MIN_REFERRALS_REQUIRED: int = 5
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields


settings = Settings()
