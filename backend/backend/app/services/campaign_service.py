from typing import Optional, List
from datetime import datetime, timedelta
import logging
from decimal import Decimal

from app.models.campaign import Campaign, CampaignCreate, CampaignUpdate, CampaignStatus, CampaignDuration
from app.core.exceptions import NotFoundException, ValidationException, CampaignException

logger = logging.getLogger(__name__)


class CampaignService:
    def __init__(self, supabase):
        self.supabase = supabase

    async def create_campaign(self, user_id: int, campaign_data: CampaignCreate) -> Campaign:
        """Create a new campaign"""
        try:
            # Calculate end date based on duration
            start_date = datetime.utcnow()
            duration_days = int(campaign_data.duration_months) * 30
            end_date = start_date + timedelta(days=duration_days)
            
            # Create campaign data
            campaign_dict = {
                "user_id": user_id,
                "title": campaign_data.title,
                "description": campaign_data.description,
                "goal_amount": float(campaign_data.goal_amount),
                "current_amount": 0.0,
                "status": "draft",
                "duration_months": campaign_data.duration_months,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "category": campaign_data.category,
                "image_url": campaign_data.image_url,
                "video_url": campaign_data.video_url,
                "story": campaign_data.story,
                "is_featured": False,
                "referral_requirement_met": False,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Insert campaign into database
            result = self.supabase.table("campaigns").insert(campaign_dict).execute()
            
            if not result.data:
                raise ValidationException("Failed to create campaign")
            
            campaign_data_dict = result.data[0]
            return Campaign(**campaign_data_dict)
            
        except Exception as e:
            logger.error(f"Error creating campaign: {e}")
            raise ValidationException(f"Failed to create campaign: {str(e)}")

    async def get_campaign_by_id(self, campaign_id: int) -> Optional[Campaign]:
        """Get campaign by ID"""
        try:
            result = self.supabase.table("campaigns").select("*").eq("id", campaign_id).execute()
            
            if not result.data:
                return None
            
            return Campaign(**result.data[0])
        except Exception as e:
            logger.error(f"Error getting campaign by ID: {e}")
            return None

    async def get_campaigns(
        self,
        status: Optional[CampaignStatus] = None,
        category: Optional[str] = None,
        featured: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Campaign]:
        """Get campaigns with filters"""
        try:
            query = self.supabase.table("campaigns").select("*")
            
            if status:
                query = query.eq("status", status.value)
            if category:
                query = query.eq("category", category)
            if featured is not None:
                query = query.eq("is_featured", featured)
            
            query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
            result = query.execute()
            
            campaigns = []
            if result.data:
                for campaign_data in result.data:
                    campaigns.append(Campaign(**campaign_data))
            
            return campaigns
        except Exception as e:
            logger.error(f"Error getting campaigns: {e}")
            return []

    async def get_user_campaigns(self, user_id: int) -> List[Campaign]:
        """Get campaigns for a specific user"""
        try:
            result = self.supabase.table("campaigns").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            
            campaigns = []
            if result.data:
                for campaign_data in result.data:
                    campaigns.append(Campaign(**campaign_data))
            
            return campaigns
        except Exception as e:
            logger.error(f"Error getting user campaigns: {e}")
            return []

    async def update_campaign(self, campaign_id: int, campaign_data: CampaignUpdate) -> Optional[Campaign]:
        """Update campaign"""
        try:
            update_dict = {}
            
            if campaign_data.title:
                update_dict["title"] = campaign_data.title
            if campaign_data.description:
                update_dict["description"] = campaign_data.description
            if campaign_data.goal_amount:
                update_dict["goal_amount"] = float(campaign_data.goal_amount)
            if campaign_data.category:
                update_dict["category"] = campaign_data.category
            if campaign_data.image_url:
                update_dict["image_url"] = campaign_data.image_url
            if campaign_data.video_url:
                update_dict["video_url"] = campaign_data.video_url
            if campaign_data.story:
                update_dict["story"] = campaign_data.story
            if campaign_data.status:
                update_dict["status"] = campaign_data.status.value
            
            update_dict["updated_at"] = datetime.utcnow().isoformat()
            
            result = self.supabase.table("campaigns").update(update_dict).eq("id", campaign_id).execute()
            
            if not result.data:
                return None
            
            return Campaign(**result.data[0])
        except Exception as e:
            logger.error(f"Error updating campaign: {e}")
            return None

    async def delete_campaign(self, campaign_id: int) -> bool:
        """Delete campaign"""
        try:
            result = self.supabase.table("campaigns").delete().eq("id", campaign_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error deleting campaign: {e}")
            return False

    async def start_campaign(self, campaign_id: int) -> bool:
        """Start a campaign"""
        try:
            # Check if campaign exists and is in draft status
            campaign = await self.get_campaign_by_id(campaign_id)
            if not campaign:
                raise NotFoundException("Campaign not found")
            
            if campaign.status != CampaignStatus.DRAFT:
                raise CampaignException("Campaign is not in draft status")
            
            # Update campaign status to active
            result = self.supabase.table("campaigns").update({
                "status": CampaignStatus.ACTIVE.value,
                "start_date": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", campaign_id).execute()
            
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error starting campaign: {e}")
            return False

    async def check_referral_requirements(self, user_id: int) -> bool:
        """Check if user has met referral requirements"""
        try:
            # Get user's referral count
            result = self.supabase.table("users").select("referral_count").eq("id", user_id).execute()
            
            if not result.data:
                return False
            
            referral_count = result.data[0].get("referral_count", 0)
            return referral_count >= 5  # Minimum 5 referrals required
        except Exception as e:
            logger.error(f"Error checking referral requirements: {e}")
            return False

    async def calculate_days_remaining(self, campaign: Campaign) -> Optional[int]:
        """Calculate days remaining for a campaign"""
        try:
            if not campaign.end_date:
                return None
            
            end_date = datetime.fromisoformat(campaign.end_date.replace('Z', '+00:00'))
            now = datetime.utcnow()
            
            if end_date <= now:
                return 0
            
            return (end_date - now).days
        except Exception as e:
            logger.error(f"Error calculating days remaining: {e}")
            return None

    async def get_donor_count(self, campaign_id: int) -> int:
        """Get number of donors for a campaign"""
        try:
            result = self.supabase.table("campaign_payments").select("id", count="exact").eq("campaign_id", campaign_id).execute()
            return result.count if result.count else 0
        except Exception as e:
            logger.error(f"Error getting donor count: {e}")
            return 0

    async def update_campaign_amount(self, campaign_id: int, amount: Decimal) -> bool:
        """Update campaign current amount"""
        try:
            # Get current amount
            result = self.supabase.table("campaigns").select("current_amount").eq("id", campaign_id).execute()
            
            if not result.data:
                return False
            
            current_amount = Decimal(str(result.data[0]["current_amount"]))
            new_amount = current_amount + amount
            
            # Update amount
            self.supabase.table("campaigns").update({
                "current_amount": float(new_amount),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", campaign_id).execute()
            
            return True
        except Exception as e:
            logger.error(f"Error updating campaign amount: {e}")
            return False
