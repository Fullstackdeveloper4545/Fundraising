from typing import Optional, List
from datetime import datetime
import logging

from app.models.shoutout import Shoutout, ShoutoutCreate
from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)


class ShoutoutService:
    def __init__(self, supabase):
        self.supabase = supabase

    async def create_shoutout(self, shoutout_data: ShoutoutCreate, donor_id: Optional[int] = None) -> Shoutout:
        """Create a new shoutout"""
        try:
            # Create shoutout data
            shoutout_dict = {
                "campaign_id": shoutout_data.campaign_id,
                "donor_id": donor_id,
                "display_name": shoutout_data.display_name,
                "message": shoutout_data.message,
                "visible": True,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Insert shoutout into database
            result = self.supabase.table("shoutouts").insert(shoutout_dict).execute()
            
            if not result.data:
                raise ValidationException("Failed to create shoutout")
            
            shoutout_data_dict = result.data[0]
            return Shoutout(**shoutout_data_dict)
            
        except Exception as e:
            logger.error(f"Error creating shoutout: {e}")
            raise ValidationException(f"Failed to create shoutout: {str(e)}")

    async def get_campaign_shoutouts(self, campaign_id: int) -> List[Shoutout]:
        """Get shoutouts for a specific campaign"""
        try:
            result = self.supabase.table("shoutouts").select("*").eq("campaign_id", campaign_id).eq("visible", True).order("created_at", desc=True).execute()
            
            shoutouts = []
            if result.data:
                for shoutout_data in result.data:
                    shoutouts.append(Shoutout(**shoutout_data))
            
            return shoutouts
        except Exception as e:
            logger.error(f"Error getting campaign shoutouts: {e}")
            return []
