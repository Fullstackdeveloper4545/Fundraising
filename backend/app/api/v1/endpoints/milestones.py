from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import logging

from app.core.database import get_supabase
from app.core.auth import get_current_user
from app.models.user import User
from app.models.milestone import Milestone, MilestoneCreate, MilestoneResponse
from app.services.milestone_service import MilestoneService
from app.core.exceptions import NotFoundException, ValidationException

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=MilestoneResponse)
async def create_milestone(
    milestone_data: MilestoneCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new milestone"""
    try:
        supabase = get_supabase()
        milestone_service = MilestoneService(supabase)
        
        # Only campaign owners and admins can create milestones
        if current_user.role not in ("admin", "student"):
            raise HTTPException(status_code=403, detail="Only campaign owners and admins can create milestones")
        
        # Create milestone
        milestone = await milestone_service.create_milestone(milestone_data)
        
        return MilestoneResponse(
            id=milestone.id,
            campaign_id=milestone.campaign_id,
            title=milestone.title,
            threshold_amount=milestone.threshold_amount,
            achieved_at=milestone.achieved_at,
            is_auto=milestone.is_auto,
            created_at=milestone.created_at,
            is_achieved=milestone.achieved_at is not None
        )
    except Exception as e:
        logger.error(f"Error creating milestone: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/campaign/{campaign_id}", response_model=List[MilestoneResponse])
async def get_campaign_milestones(campaign_id: int):
    """Get milestones for a specific campaign"""
    try:
        supabase = get_supabase()
        milestone_service = MilestoneService(supabase)
        
        milestones = await milestone_service.get_campaign_milestones(campaign_id)
        
        milestone_responses = []
        for milestone in milestones:
            milestone_responses.append(MilestoneResponse(
                id=milestone.id,
                campaign_id=milestone.campaign_id,
                title=milestone.title,
                threshold_amount=milestone.threshold_amount,
                achieved_at=milestone.achieved_at,
                is_auto=milestone.is_auto,
                created_at=milestone.created_at,
                is_achieved=milestone.achieved_at is not None
            ))
        
        return milestone_responses
    except Exception as e:
        logger.error(f"Error getting campaign milestones: {e}")
        raise HTTPException(status_code=400, detail=str(e))
