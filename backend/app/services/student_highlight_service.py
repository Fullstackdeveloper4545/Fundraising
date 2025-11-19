from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

from app.core.exceptions import NotFoundException, ValidationException

logger = logging.getLogger(__name__)


class StudentHighlightService:
    """Service for managing student highlights and achievements"""
    
    def __init__(self, supabase):
        self.supabase = supabase

    async def get_current_highlighted_student(self) -> Optional[Dict[str, Any]]:
        """Get the currently highlighted student"""
        try:
            # Get the most recent highlighted student
            result = self.supabase.table("student_highlights").select(
                "*, users(first_name, last_name)"
            ).eq("is_active", True).order("created_at", desc=True).limit(1).execute()
            
            if not result.data:
                return None
            
            highlight_data = result.data[0]
            return {
                "id": highlight_data["id"],
                "student_name": f"{highlight_data['users']['first_name']} {highlight_data['users']['last_name']}",
                "achievement": highlight_data["achievement"],
                "description": highlight_data["description"],
                "image_url": highlight_data["image_url"],
                "highlighted_at": highlight_data["created_at"]
            }
        except Exception as e:
            logger.error(f"Error getting highlighted student: {e}")
            return None

    async def create_student_highlight(
        self,
        user_id: int,
        achievement: str,
        description: str,
        image_url: Optional[str] = None
    ) -> bool:
        """Create a new student highlight"""
        try:
            # Deactivate current highlights
            self.supabase.table("student_highlights").update({
                "is_active": False
            }).eq("is_active", True).execute()
            
            # Create new highlight
            highlight_dict = {
                "user_id": user_id,
                "achievement": achievement,
                "description": description,
                "image_url": image_url,
                "is_active": True,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("student_highlights").insert(highlight_dict).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error creating student highlight: {e}")
            return False

    async def get_highlighted_donors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get list of highlighted donors (without revealing amounts)"""
        try:
            # Get recent large donations (anonymized)
            result = self.supabase.table("campaign_payments").select(
                "donor_name, display_name, created_at, campaigns(title)"
            ).eq("is_anonymous", False).order("created_at", desc=True).limit(limit).execute()
            
            highlighted_donors = []
            if result.data:
                for payment in result.data:
                    highlighted_donors.append({
                        "donor_name": payment.get("donor_name") or payment.get("display_name") or "Anonymous",
                        "campaign_title": payment["campaigns"]["title"],
                        "donated_at": payment["created_at"]
                    })
            
            return highlighted_donors
        except Exception as e:
            logger.error(f"Error getting highlighted donors: {e}")
            return []

    async def get_student_achievements(self, user_id: int) -> List[Dict[str, Any]]:
        """Get achievements for a specific student"""
        try:
            result = self.supabase.table("student_highlights").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            
            achievements = []
            if result.data:
                for highlight in result.data:
                    achievements.append({
                        "id": highlight["id"],
                        "achievement": highlight["achievement"],
                        "description": highlight["description"],
                        "image_url": highlight["image_url"],
                        "is_active": highlight["is_active"],
                        "created_at": highlight["created_at"]
                    })
            
            return achievements
        except Exception as e:
            logger.error(f"Error getting student achievements: {e}")
            return []

    async def get_weekly_highlights(self) -> List[Dict[str, Any]]:
        """Get weekly student highlights"""
        try:
            # Get highlights from the past week
            week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
            
            result = self.supabase.table("student_highlights").select(
                "*, users(first_name, last_name)"
            ).gte("created_at", week_ago).order("created_at", desc=True).execute()
            
            highlights = []
            if result.data:
                for highlight in result.data:
                    highlights.append({
                        "id": highlight["id"],
                        "student_name": f"{highlight['users']['first_name']} {highlight['users']['last_name']}",
                        "achievement": highlight["achievement"],
                        "description": highlight["description"],
                        "image_url": highlight["image_url"],
                        "created_at": highlight["created_at"]
                    })
            
            return highlights
        except Exception as e:
            logger.error(f"Error getting weekly highlights: {e}")
            return []
