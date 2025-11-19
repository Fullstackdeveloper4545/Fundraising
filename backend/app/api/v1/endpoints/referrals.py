from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import logging

from app.core.database import get_supabase
from app.core.auth import get_current_user
from app.models.user import User
from app.models.referral import Referral, ReferralCreate, ReferralResponse, ReferralStats
from app.services.referral_service import ReferralService
from app.core.exceptions import NotFoundException, ValidationException

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ReferralResponse)
async def create_referral(
    referral_data: ReferralCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new referral"""
    try:
        supabase = get_supabase()
        referral_service = ReferralService(supabase)
        
        # Only students can create referrals
        if current_user.role != "student":
            raise HTTPException(status_code=403, detail="Only student users can create referrals")

        # Ensure the campaign belongs to the current student
        campaign_result = supabase.table("campaigns").select("user_id").eq("id", referral_data.campaign_id).single().execute()
        if not campaign_result.data:
            raise NotFoundException("Campaign not found")
        if campaign_result.data["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to create referrals for this campaign")

        # Create referral
        referral = await referral_service.create_referral(referral_data)
        
        return ReferralResponse(
            id=referral.id,
            campaign_id=referral.campaign_id,
            invited_email=referral.invited_email,
            invited_phone=referral.invited_phone,
            token=referral.token,
            status=referral.status,
            sent_at=referral.sent_at,
            accepted_at=referral.accepted_at,
            created_at=referral.created_at
        )
    except Exception as e:
        logger.error(f"Error creating referral: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/campaign/{campaign_id}", response_model=List[ReferralResponse])
async def get_campaign_referrals(
    campaign_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get referrals for a specific campaign"""
    try:
        supabase = get_supabase()
        referral_service = ReferralService(supabase)
        
        # Check if user is authorized to view referrals (campaign owner or admin)
        campaign_result = supabase.table("campaigns").select("user_id").eq("id", campaign_id).single().execute()
        if not campaign_result.data:
            raise NotFoundException("Campaign not found")
        
        campaign_owner_id = campaign_result.data["user_id"]
        if campaign_owner_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to view these referrals")
        
        referrals = await referral_service.get_campaign_referrals(campaign_id)
        
        referral_responses = []
        for referral in referrals:
            referral_responses.append(ReferralResponse(
                id=referral.id,
                campaign_id=referral.campaign_id,
                invited_email=referral.invited_email,
                invited_phone=referral.invited_phone,
                token=referral.token,
                status=referral.status,
                sent_at=referral.sent_at,
                accepted_at=referral.accepted_at,
                created_at=referral.created_at
            ))
        
        return referral_responses
    except Exception as e:
        logger.error(f"Error getting campaign referrals: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats/{campaign_id}", response_model=ReferralStats)
async def get_referral_stats(
    campaign_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get referral statistics for a campaign"""
    try:
        supabase = get_supabase()
        referral_service = ReferralService(supabase)
        
        # Check if user is authorized to view referral stats (campaign owner or admin)
        campaign_result = supabase.table("campaigns").select("user_id").eq("id", campaign_id).single().execute()
        if not campaign_result.data:
            raise NotFoundException("Campaign not found")
        
        campaign_owner_id = campaign_result.data["user_id"]
        if campaign_owner_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to view these referral stats")
        
        stats = await referral_service.get_referral_stats(campaign_id)
        return stats
    except Exception as e:
        logger.error(f"Error getting referral stats: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/accept/{token}")
async def accept_referral(token: str):
    """Accept a referral invitation"""
    try:
        supabase = get_supabase()
        referral_service = ReferralService(supabase)
        
        result = await referral_service.accept_referral(token)
        if not result:
            raise ValidationException("Invalid or expired referral token")
        
        return {"message": "Referral accepted successfully"}
    except Exception as e:
        logger.error(f"Error accepting referral: {e}")
        raise HTTPException(status_code=400, detail=str(e))
