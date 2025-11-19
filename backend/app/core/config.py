from pydantic_settings import BaseSettings
from typing import List, Optional
from urllib.parse import urlparse
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
    ADDITIONAL_ALLOWED_ORIGINS: Optional[str] = None

    # Trusted hosts for FastAPI TrustedHostMiddleware
    TRUSTED_HOSTS: List[str] = [
        "localhost",
        "127.0.0.1",
        "*.vercel.app",
        "*.netlify.app",
        "srv1133545.hstgr.cloud",
        "72.61.174.202",
    ]
    ADDITIONAL_TRUSTED_HOSTS: Optional[str] = None
    
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

    @staticmethod
    def _normalize_origin(origin: str) -> str:
        return origin.rstrip("/") if origin else origin

    def get_allowed_origins(self) -> List[str]:
        """Combine default, frontend, and optionally configured origins."""
        origins = {self._normalize_origin(origin) for origin in (self.ALLOWED_ORIGINS or []) if origin}

        frontend_origin = self._normalize_origin(self.FRONTEND_URL)
        if frontend_origin:
            origins.add(frontend_origin)

        extra_raw = self.ADDITIONAL_ALLOWED_ORIGINS or os.getenv("EXTRA_ALLOWED_ORIGINS")
        if extra_raw:
            for origin in extra_raw.split(","):
                normalized = self._normalize_origin(origin.strip())
                if normalized:
                    origins.add(normalized)

        return sorted(origins)

    def get_trusted_hosts(self) -> List[str]:
        """Combine default hosts with those derived from configured URLs or overrides."""
        hosts = {host.strip() for host in (self.TRUSTED_HOSTS or []) if host and host.strip()}

        def _add_host_from_url(url: Optional[str]) -> None:
            if not url:
                return
            try:
                parsed = urlparse(url)
                if parsed.hostname:
                    hosts.add(parsed.hostname)
            except ValueError:
                return

        _add_host_from_url(self.FRONTEND_URL)
        _add_host_from_url(self.BACKEND_URL)

        extra_hosts = self.ADDITIONAL_TRUSTED_HOSTS or os.getenv("EXTRA_TRUSTED_HOSTS")
        if extra_hosts:
            for host in extra_hosts.split(","):
                cleaned = host.strip()
                if cleaned:
                    hosts.add(cleaned)

        return sorted(hosts)


settings = Settings()
