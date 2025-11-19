from typing import Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AdminService:
    def __init__(self, supabase):
        self.supabase = supabase

    async def get_platform_stats(self) -> Dict[str, Any]:
        """Get platform statistics"""
        try:
            # Get total users
            users_result = self.supabase.table("users").select("id", count="exact").execute()
            total_users = users_result.count if users_result.count else 0
            
            # Get total campaigns
            campaigns_result = self.supabase.table("campaigns").select("id", count="exact").execute()
            total_campaigns = campaigns_result.count if campaigns_result.count else 0
            
            # Get total donations
            payments_result = self.supabase.table("campaign_payments").select("amount").execute()
            total_donations = sum(float(payment["amount"]) for payment in payments_result.data) if payments_result.data else 0.0
            
            # Get active campaigns
            active_campaigns_result = self.supabase.table("campaigns").select("id", count="exact").eq("status", "active").execute()
            active_campaigns = active_campaigns_result.count if active_campaigns_result.count else 0
            
            return {
                "total_users": total_users,
                "total_campaigns": total_campaigns,
                "total_donations": total_donations,
                "active_campaigns": active_campaigns
            }
        except Exception as e:
            logger.error(f"Error getting platform stats: {e}")
            return {
                "total_users": 0,
                "total_campaigns": 0,
                "total_donations": 0.0,
                "active_campaigns": 0
            }

    async def get_all_campaigns(self) -> List[Dict[str, Any]]:
        """Get all campaigns for admin"""
        try:
            result = self.supabase.table("campaigns").select("*, users(*)").order("created_at", desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting all campaigns: {e}")
            return []

    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users for admin"""
        try:
            result = self.supabase.table("users").select("*").order("created_at", desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    async def feature_campaign(self, campaign_id: int) -> bool:
        """Feature a campaign"""
        try:
            result = self.supabase.table("campaigns").update({
                "is_featured": True,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", campaign_id).execute()
            
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error featuring campaign: {e}")
            return False

    async def close_campaign_permanently(self, campaign_id: int) -> bool:
        """Permanently close a campaign (set status to 'closed' and disable featuring).
        Returns True only if exactly one row was updated.
        """
        try:
            # Ensure campaign exists and not already closed
            existing = self.supabase.table("campaigns").select("id,status").eq("id", campaign_id).single().execute()
            if not existing.data:
                return False
            if existing.data.get("status") == "closed":
                return True

            result = self.supabase.table("campaigns").update({
                "status": "closed",
                "is_featured": False,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", campaign_id).execute()

            return bool(result.data) and len(result.data) == 1
        except Exception as e:
            logger.error(f"Error closing campaign {campaign_id}: {e}")
            return False

    async def update_campaign_status(self, campaign_id: int, status: str) -> bool:
        """Update campaign status to one of the allowed enum values."""
        try:
            existing = self.supabase.table("campaigns").select("id").eq("id", campaign_id).single().execute()
            if not existing.data:
                return False
            result = self.supabase.table("campaigns").update({
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", campaign_id).execute()
            return bool(result.data) and len(result.data) == 1
        except Exception as e:
            logger.error(f"Error updating campaign {campaign_id} status to {status}: {e}")
            return False
