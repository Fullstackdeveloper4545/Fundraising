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

    # ===== COMPREHENSIVE ADMIN CRUD METHODS =====

    # User Management
    async def update_user(self, user_id: int, user_data: dict) -> bool:
        """Update any user (admin only)"""
        try:
            user_data["updated_at"] = datetime.utcnow().isoformat()
            result = self.supabase.table("users").update(user_data).eq("id", user_id).execute()
            return bool(result.data) and len(result.data) == 1
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return False

    async def delete_user(self, user_id: int) -> bool:
        """Delete any user (admin only)"""
        try:
            result = self.supabase.table("users").delete().eq("id", user_id).execute()
            return bool(result.data) and len(result.data) == 1
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False

    # Campaign Management
    async def update_campaign(self, campaign_id: int, campaign_data: dict) -> bool:
        """Update any campaign (admin only)"""
        try:
            campaign_data["updated_at"] = datetime.utcnow().isoformat()
            result = self.supabase.table("campaigns").update(campaign_data).eq("id", campaign_id).execute()
            return bool(result.data) and len(result.data) == 1
        except Exception as e:
            logger.error(f"Error updating campaign {campaign_id}: {e}")
            return False

    async def delete_campaign(self, campaign_id: int) -> bool:
        """Delete any campaign (admin only)"""
        try:
            result = self.supabase.table("campaigns").delete().eq("id", campaign_id).execute()
            return bool(result.data) and len(result.data) == 1
        except Exception as e:
            logger.error(f"Error deleting campaign {campaign_id}: {e}")
            return False

    # Payment Management
    async def get_all_payments(self) -> List[Dict[str, Any]]:
        """Get all payments for admin"""
        try:
            result = self.supabase.table("campaign_payments").select("*, campaigns(*), users(*)").order("created_at", desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting all payments: {e}")
            return []

    async def update_payment(self, payment_id: int, payment_data: dict) -> bool:
        """Update any payment (admin only)"""
        try:
            payment_data["updated_at"] = datetime.utcnow().isoformat()
            result = self.supabase.table("campaign_payments").update(payment_data).eq("id", payment_id).execute()
            return bool(result.data) and len(result.data) == 1
        except Exception as e:
            logger.error(f"Error updating payment {payment_id}: {e}")
            return False

    async def delete_payment(self, payment_id: int) -> bool:
        """Delete any payment (admin only)"""
        try:
            result = self.supabase.table("campaign_payments").delete().eq("id", payment_id).execute()
            return bool(result.data) and len(result.data) == 1
        except Exception as e:
            logger.error(f"Error deleting payment {payment_id}: {e}")
            return False

    # Company Management
    async def update_company(self, company_id: int, company_data: dict) -> bool:
        """Update any company (admin only)"""
        try:
            company_data["updated_at"] = datetime.utcnow().isoformat()
            result = self.supabase.table("companies").update(company_data).eq("id", company_id).execute()
            return bool(result.data) and len(result.data) == 1
        except Exception as e:
            logger.error(f"Error updating company {company_id}: {e}")
            return False

    async def delete_company(self, company_id: int) -> bool:
        """Delete any company (admin only)"""
        try:
            result = self.supabase.table("companies").delete().eq("id", company_id).execute()
            return bool(result.data) and len(result.data) == 1
        except Exception as e:
            logger.error(f"Error deleting company {company_id}: {e}")
            return False

    # Milestone Management
    async def get_all_milestones(self) -> List[Dict[str, Any]]:
        """Get all milestones for admin"""
        try:
            result = self.supabase.table("milestones").select("*, campaigns(*)").order("created_at", desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting all milestones: {e}")
            return []

    async def update_milestone(self, milestone_id: int, milestone_data: dict) -> bool:
        """Update any milestone (admin only)"""
        try:
            milestone_data["updated_at"] = datetime.utcnow().isoformat()
            result = self.supabase.table("milestones").update(milestone_data).eq("id", milestone_id).execute()
            return bool(result.data) and len(result.data) == 1
        except Exception as e:
            logger.error(f"Error updating milestone {milestone_id}: {e}")
            return False

    async def delete_milestone(self, milestone_id: int) -> bool:
        """Delete any milestone (admin only)"""
        try:
            result = self.supabase.table("milestones").delete().eq("id", milestone_id).execute()
            return bool(result.data) and len(result.data) == 1
        except Exception as e:
            logger.error(f"Error deleting milestone {milestone_id}: {e}")
            return False

    # Receipt Management
    async def get_all_receipts(self) -> List[Dict[str, Any]]:
        """Get all receipts for admin"""
        try:
            result = self.supabase.table("receipts").select("*, campaign_payments(*)").order("generated_at", desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting all receipts: {e}")
            return []

    async def delete_receipt(self, receipt_id: int) -> bool:
        """Delete any receipt (admin only)"""
        try:
            result = self.supabase.table("receipts").delete().eq("id", receipt_id).execute()
            return bool(result.data) and len(result.data) == 1
        except Exception as e:
            logger.error(f"Error deleting receipt {receipt_id}: {e}")
            return False

    # Referral Management
    async def get_all_referrals(self) -> List[Dict[str, Any]]:
        """Get all referrals for admin"""
        try:
            result = self.supabase.table("referrals").select("*, campaigns(*)").order("created_at", desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting all referrals: {e}")
            return []

    async def update_referral(self, referral_id: int, referral_data: dict) -> bool:
        """Update any referral (admin only)"""
        try:
            referral_data["updated_at"] = datetime.utcnow().isoformat()
            result = self.supabase.table("referrals").update(referral_data).eq("id", referral_id).execute()
            return bool(result.data) and len(result.data) == 1
        except Exception as e:
            logger.error(f"Error updating referral {referral_id}: {e}")
            return False

    async def delete_referral(self, referral_id: int) -> bool:
        """Delete any referral (admin only)"""
        try:
            result = self.supabase.table("referrals").delete().eq("id", referral_id).execute()
            return bool(result.data) and len(result.data) == 1
        except Exception as e:
            logger.error(f"Error deleting referral {referral_id}: {e}")
            return False

    # Shoutout Management
    async def get_all_shoutouts(self) -> List[Dict[str, Any]]:
        """Get all shoutouts for admin"""
        try:
            result = self.supabase.table("shoutouts").select("*, campaigns(*), users(*)").order("created_at", desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting all shoutouts: {e}")
            return []

    async def update_shoutout(self, shoutout_id: int, shoutout_data: dict) -> bool:
        """Update any shoutout (admin only)"""
        try:
            shoutout_data["updated_at"] = datetime.utcnow().isoformat()
            result = self.supabase.table("shoutouts").update(shoutout_data).eq("id", shoutout_id).execute()
            return bool(result.data) and len(result.data) == 1
        except Exception as e:
            logger.error(f"Error updating shoutout {shoutout_id}: {e}")
            return False

    async def delete_shoutout(self, shoutout_id: int) -> bool:
        """Delete any shoutout (admin only)"""
        try:
            result = self.supabase.table("shoutouts").delete().eq("id", shoutout_id).execute()
            return bool(result.data) and len(result.data) == 1
        except Exception as e:
            logger.error(f"Error deleting shoutout {shoutout_id}: {e}")
            return False