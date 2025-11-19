from typing import Optional, List
from datetime import datetime
import logging

from app.models.milestone import Milestone, MilestoneCreate
from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)


class MilestoneService:
    def __init__(self, supabase):
        self.supabase = supabase

    async def create_milestone(self, milestone_data: MilestoneCreate) -> Milestone:
        """Create a new milestone"""
        try:
            # Create milestone data
            milestone_dict = {
                "campaign_id": milestone_data.campaign_id,
                "title": milestone_data.title,
                "threshold_amount": float(milestone_data.threshold_amount),
                "achieved_at": None,
                "is_auto": milestone_data.is_auto,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Insert milestone into database
            result = self.supabase.table("milestones").insert(milestone_dict).execute()
            
            if not result.data:
                raise ValidationException("Failed to create milestone")
            
            milestone_data_dict = result.data[0]
            return Milestone(**milestone_data_dict)
            
        except Exception as e:
            logger.error(f"Error creating milestone: {e}")
            raise ValidationException(f"Failed to create milestone: {str(e)}")

    async def get_campaign_milestones(self, campaign_id: int) -> List[Milestone]:
        """Get milestones for a specific campaign"""
        try:
            result = self.supabase.table("milestones").select("*").eq("campaign_id", campaign_id).order("threshold_amount", desc=False).execute()
            
            milestones = []
            if result.data:
                for milestone_data in result.data:
                    milestones.append(Milestone(**milestone_data))
            
            return milestones
        except Exception as e:
            logger.error(f"Error getting campaign milestones: {e}")
            return []
