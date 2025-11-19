from typing import Optional, List
from datetime import datetime
import logging

from app.models.referral import Referral, ReferralCreate, ReferralStats, ReferralStatus
from app.core.security import generate_referral_token
from app.core.exceptions import NotFoundException, ValidationException

logger = logging.getLogger(__name__)


class ReferralService:
    def __init__(self, supabase):
        self.supabase = supabase

    async def create_referral(self, referral_data: ReferralCreate) -> Referral:
        """Create a new referral"""
        try:
            # Generate unique referral token
            token = generate_referral_token()
            
            # Create referral data
            referral_dict = {
                "campaign_id": referral_data.campaign_id,
                "invited_email": referral_data.invited_email,
                "invited_phone": referral_data.invited_phone,
                "token": token,
                "status": ReferralStatus.SENT.value,
                "sent_at": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Insert referral into database
            result = self.supabase.table("referrals").insert(referral_dict).execute()
            
            if not result.data:
                raise ValidationException("Failed to create referral")
            
            referral_data_dict = result.data[0]
            return Referral(**referral_data_dict)
            
        except Exception as e:
            logger.error(f"Error creating referral: {e}")
            raise ValidationException(f"Failed to create referral: {str(e)}")

    async def get_campaign_referrals(self, campaign_id: int) -> List[Referral]:
        """Get referrals for a specific campaign"""
        try:
            result = self.supabase.table("referrals").select("*").eq("campaign_id", campaign_id).order("created_at", desc=True).execute()
            
            referrals = []
            if result.data:
                for referral_data in result.data:
                    referrals.append(Referral(**referral_data))
            
            return referrals
        except Exception as e:
            logger.error(f"Error getting campaign referrals: {e}")
            return []

    async def get_referral_by_token(self, token: str) -> Optional[Referral]:
        """Get referral by token"""
        try:
            result = self.supabase.table("referrals").select("*").eq("token", token).execute()
            
            if not result.data:
                return None
            
            return Referral(**result.data[0])
        except Exception as e:
            logger.error(f"Error getting referral by token: {e}")
            return None

    async def accept_referral(self, token: str) -> bool:
        """Accept a referral invitation"""
        try:
            # Get referral by token
            referral = await self.get_referral_by_token(token)
            if not referral:
                return False
            
            # Check if referral is already accepted or expired
            if referral.status != ReferralStatus.SENT:
                return False
            
            # Update referral status to accepted
            result = self.supabase.table("referrals").update({
                "status": ReferralStatus.ACCEPTED.value,
                "accepted_at": datetime.utcnow().isoformat()
            }).eq("token", token).execute()
            
            if result.data:
                # Update user's referral count
                await self._update_user_referral_count(referral.campaign_id)
                
                # Update campaign referral count and check if it should be promoted
                from app.services.campaign_service import CampaignService
                campaign_service = CampaignService(self.supabase)
                await campaign_service.update_campaign_referral_count(referral.campaign_id)
            
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error accepting referral: {e}")
            return False

    async def _update_user_referral_count(self, campaign_id: int):
        """Update user's referral count when referral is accepted"""
        try:
            # Get campaign to find user_id
            campaign_result = self.supabase.table("campaigns").select("user_id").eq("id", campaign_id).execute()
            
            if not campaign_result.data:
                return False
            
            user_id = campaign_result.data[0]["user_id"]
            
            # Get current referral count
            user_result = self.supabase.table("users").select("referral_count").eq("id", user_id).execute()
            
            if not user_result.data:
                return False
            
            current_count = user_result.data[0].get("referral_count", 0)
            new_count = current_count + 1
            
            # Update referral count
            self.supabase.table("users").update({
                "referral_count": new_count,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            return True
        except Exception as e:
            logger.error(f"Error updating user referral count: {e}")
            return False

    async def get_referral_stats(self, campaign_id: int) -> ReferralStats:
        """Get referral statistics for a campaign"""
        try:
            # Get all referrals for campaign
            result = self.supabase.table("referrals").select("status").eq("campaign_id", campaign_id).execute()
            
            if not result.data:
                return ReferralStats(
                    total_sent=0,
                    total_accepted=0,
                    total_expired=0,
                    acceptance_rate=0.0
                )
            
            total_sent = len(result.data)
            total_accepted = len([r for r in result.data if r["status"] == ReferralStatus.ACCEPTED.value])
            total_expired = len([r for r in result.data if r["status"] == ReferralStatus.EXPIRED.value])
            
            acceptance_rate = (total_accepted / total_sent * 100) if total_sent > 0 else 0.0
            
            return ReferralStats(
                total_sent=total_sent,
                total_accepted=total_accepted,
                total_expired=total_expired,
                acceptance_rate=acceptance_rate
            )
        except Exception as e:
            logger.error(f"Error getting referral stats: {e}")
            return ReferralStats(
                total_sent=0,
                total_accepted=0,
                total_expired=0,
                acceptance_rate=0.0
            )
