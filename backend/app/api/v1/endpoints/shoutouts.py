from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import logging

from app.core.database import get_supabase
from app.core.auth import get_current_user
from app.models.user import User
from app.models.shoutout import Shoutout, ShoutoutCreate, ShoutoutResponse
from app.services.shoutout_service import ShoutoutService
from app.core.exceptions import NotFoundException, ValidationException

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ShoutoutResponse)
async def create_shoutout(
    shoutout_data: ShoutoutCreate,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Create a new shoutout"""
    try:
        supabase = get_supabase()
        shoutout_service = ShoutoutService(supabase)
        
        # Set donor_id if user is logged in
        donor_id = current_user.id if current_user else None
        
        # Create shoutout
        shoutout = await shoutout_service.create_shoutout(shoutout_data, donor_id)
        
        return ShoutoutResponse(
            id=shoutout.id,
            campaign_id=shoutout.campaign_id,
            donor_id=shoutout.donor_id,
            display_name=shoutout.display_name,
            message=shoutout.message,
            visible=shoutout.visible,
            created_at=shoutout.created_at
        )
    except Exception as e:
        logger.error(f"Error creating shoutout: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/campaign/{campaign_id}", response_model=List[ShoutoutResponse])
async def get_campaign_shoutouts(campaign_id: int):
    """Get shoutouts for a specific campaign"""
    try:
        supabase = get_supabase()
        shoutout_service = ShoutoutService(supabase)
        
        shoutouts = await shoutout_service.get_campaign_shoutouts(campaign_id)
        
        shoutout_responses = []
        for shoutout in shoutouts:
            shoutout_responses.append(ShoutoutResponse(
                id=shoutout.id,
                campaign_id=shoutout.campaign_id,
                donor_id=shoutout.donor_id,
                display_name=shoutout.display_name,
                message=shoutout.message,
                visible=shoutout.visible,
                created_at=shoutout.created_at
            ))
        
        return shoutout_responses
    except Exception as e:
        logger.error(f"Error getting campaign shoutouts: {e}")
        raise HTTPException(status_code=400, detail=str(e))
