from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import logging

from app.core.database import get_supabase, get_supabase_admin
from app.core.auth import get_current_user
from app.models.user import User
from app.models.campaign import CampaignStatus
from app.services.admin_service import AdminService
from app.core.exceptions import AuthorizationException

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure user is admin"""
    if current_user.role != "admin":
        raise AuthorizationException("Admin access required")
    return current_user


@router.get("/stats")
async def get_platform_stats(admin_user: User = Depends(get_admin_user)):
    """Get platform statistics"""
    try:
        # Use admin client to bypass RLS for admin operations
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        stats = await admin_service.get_platform_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting platform stats: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/campaigns")
async def get_all_campaigns(admin_user: User = Depends(get_admin_user)):
    """Get all campaigns for admin"""
    try:
        # Use admin client to bypass RLS for admin operations
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        campaigns = await admin_service.get_all_campaigns()
        return campaigns
    except Exception as e:
        logger.error(f"Error getting all campaigns: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/campaigns/{campaign_id}/feature")
async def feature_campaign(
    campaign_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """Feature a campaign"""
    try:
        # Use admin client to avoid RLS limitations on listing
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        result = await admin_service.feature_campaign(campaign_id)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to feature campaign")
        
        return {"message": "Campaign featured successfully"}
    except Exception as e:
        logger.error(f"Error featuring campaign: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/campaigns/{campaign_id}/close")
async def close_campaign(
    campaign_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """Permanently close a campaign."""
    try:
        # Use admin client to bypass RLS for admin operations
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)

        result = await admin_service.close_campaign_permanently(campaign_id)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to close campaign")

        return {"message": "Campaign closed permanently"}
    except Exception as e:
        logger.error(f"Error closing campaign: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/campaigns/{campaign_id}/status/{status}")
async def set_campaign_status(
    campaign_id: int,
    status: CampaignStatus,
    admin_user: User = Depends(get_admin_user)
):
    """Set campaign status to any valid `CampaignStatus` value."""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)

        ok = await admin_service.update_campaign_status(campaign_id, status.value)
        if not ok:
            raise HTTPException(status_code=400, detail="Failed to update status")
        return {"message": f"Campaign status set to {status.value}"}
    except Exception as e:
        logger.error(f"Error setting campaign status: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users")
async def get_all_users(admin_user: User = Depends(get_admin_user)):
    """Get all users for admin"""
    try:
        supabase = get_supabase()
        admin_service = AdminService(supabase)
        
        users = await admin_service.get_all_users()
        return users
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        raise HTTPException(status_code=400, detail=str(e))
