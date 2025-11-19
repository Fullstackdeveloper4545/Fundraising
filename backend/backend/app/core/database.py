from supabase import create_client, Client
from app.core.config import settings
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

# Global Supabase client
supabase: Client = None


async def init_db():
    """Initialize database connection"""
    global supabase
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase credentials not provided. Database connection will not be available.")
            return
        
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Database connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def get_supabase() -> Client:
    """Get Supabase client instance"""
    if supabase is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return supabase


def get_supabase_admin() -> Client:
    """Get Supabase admin client for service operations (bypasses RLS)."""
    if not settings.SUPABASE_URL:
        logger.error("SUPABASE_URL is not set")
        raise HTTPException(status_code=500, detail="SUPABASE_URL is not configured")
    if not settings.SUPABASE_SERVICE_ROLE_KEY:
        logger.error("SUPABASE_SERVICE_ROLE_KEY is not set (cannot bypass RLS)")
        raise HTTPException(status_code=500, detail="SUPABASE_SERVICE_ROLE_KEY is not configured")
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    return client
