from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import secrets
import string

from app.core.config import settings

logger = logging.getLogger(__name__)


class OTPService:
    """Service for handling OTP (One-Time Password) operations"""
    
    def __init__(self, supabase):
        self.supabase = supabase
        self.otp_length = 6
        self.otp_expiry_minutes = 10  # OTP expires in 10 minutes
        self.max_attempts = 3  # Maximum verification attempts
    
    def generate_otp(self) -> str:
        """Generate a random OTP"""
        return ''.join(secrets.choice(string.digits) for _ in range(self.otp_length))
    
    async def create_otp(self, email: str, purpose: str = "email_verification") -> Dict[str, Any]:
        """Create and store an OTP for the given email"""
        try:
            # Generate OTP
            otp_code = self.generate_otp()
            expires_at = datetime.utcnow() + timedelta(minutes=self.otp_expiry_minutes)
            
            # Store OTP in database
            otp_data = {
                "email": email.lower(),
                "otp_code": otp_code,
                "purpose": purpose,
                "expires_at": expires_at.isoformat(),
                "attempts": 0,
                "is_used": False,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("otp_verifications").insert(otp_data).execute()
            
            if result.data:
                logger.info(f"OTP created for {email} with purpose {purpose}")
                return {
                    "otp_code": otp_code,
                    "expires_at": expires_at.isoformat(),
                    "email": email,
                    "purpose": purpose
                }
            else:
                raise Exception("Failed to create OTP")
                
        except Exception as e:
            logger.error(f"Error creating OTP for {email}: {e}")
            raise Exception(f"Failed to create OTP: {str(e)}")
    
    async def verify_otp(self, email: str, otp_code: str, purpose: str = "email_verification") -> bool:
        """Verify an OTP for the given email"""
        try:
            # Get OTP from database
            result = self.supabase.table("otp_verifications").select("*").eq("email", email.lower()).eq("purpose", purpose).eq("is_used", False).order("created_at", desc=True).limit(1).execute()
            
            if not result.data:
                logger.warning(f"No valid OTP found for {email}")
                return False
            
            otp_data = result.data[0]
            
            # Check if OTP is expired
            expires_at = datetime.fromisoformat(otp_data["expires_at"])
            if datetime.utcnow() > expires_at:
                logger.warning(f"OTP expired for {email}")
                await self._mark_otp_expired(otp_data["id"])
                return False
            
            # Check if max attempts exceeded
            if otp_data["attempts"] >= self.max_attempts:
                logger.warning(f"Max attempts exceeded for OTP {email}")
                await self._mark_otp_expired(otp_data["id"])
                return False
            
            # Verify OTP code
            if otp_data["otp_code"] == otp_code:
                # Mark OTP as used
                await self._mark_otp_used(otp_data["id"])
                logger.info(f"OTP verified successfully for {email}")
                return True
            else:
                # Increment attempts
                await self._increment_otp_attempts(otp_data["id"])
                logger.warning(f"Invalid OTP attempt for {email}")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying OTP for {email}: {e}")
            return False
    
    async def _mark_otp_used(self, otp_id: int):
        """Mark OTP as used"""
        try:
            self.supabase.table("otp_verifications").update({
                "is_used": True,
                "verified_at": datetime.utcnow().isoformat()
            }).eq("id", otp_id).execute()
        except Exception as e:
            logger.error(f"Error marking OTP as used: {e}")
    
    async def _mark_otp_expired(self, otp_id: int):
        """Mark OTP as expired"""
        try:
            self.supabase.table("otp_verifications").update({
                "is_used": True,
                "expired_at": datetime.utcnow().isoformat()
            }).eq("id", otp_id).execute()
        except Exception as e:
            logger.error(f"Error marking OTP as expired: {e}")
    
    async def _increment_otp_attempts(self, otp_id: int):
        """Increment OTP attempts"""
        try:
            # Get current attempts
            result = self.supabase.table("otp_verifications").select("attempts").eq("id", otp_id).execute()
            if result.data:
                current_attempts = result.data[0]["attempts"]
                self.supabase.table("otp_verifications").update({
                    "attempts": current_attempts + 1
                }).eq("id", otp_id).execute()
        except Exception as e:
            logger.error(f"Error incrementing OTP attempts: {e}")
    
    async def resend_otp(self, email: str, purpose: str = "email_verification") -> Dict[str, Any]:
        """Resend OTP for the given email"""
        try:
            # Mark existing OTPs as expired
            self.supabase.table("otp_verifications").update({
                "is_used": True,
                "expired_at": datetime.utcnow().isoformat()
            }).eq("email", email.lower()).eq("purpose", purpose).eq("is_used", False).execute()
            
            # Create new OTP
            return await self.create_otp(email, purpose)
            
        except Exception as e:
            logger.error(f"Error resending OTP for {email}: {e}")
            raise Exception(f"Failed to resend OTP: {str(e)}")
    
    async def cleanup_expired_otps(self):
        """Clean up expired OTPs from database"""
        try:
            current_time = datetime.utcnow().isoformat()
            result = self.supabase.table("otp_verifications").update({
                "is_used": True,
                "expired_at": current_time
            }).lt("expires_at", current_time).eq("is_used", False).execute()
            
            if result.data:
                logger.info(f"Cleaned up {len(result.data)} expired OTPs")
                
        except Exception as e:
            logger.error(f"Error cleaning up expired OTPs: {e}")
    
    async def get_otp_status(self, email: str, purpose: str = "email_verification") -> Dict[str, Any]:
        """Get OTP status for the given email"""
        try:
            result = self.supabase.table("otp_verifications").select("*").eq("email", email.lower()).eq("purpose", purpose).eq("is_used", False).order("created_at", desc=True).limit(1).execute()
            
            if not result.data:
                return {
                    "has_active_otp": False,
                    "message": "No active OTP found"
                }
            
            otp_data = result.data[0]
            expires_at = datetime.fromisoformat(otp_data["expires_at"])
            is_expired = datetime.utcnow() > expires_at
            
            return {
                "has_active_otp": not is_expired,
                "expires_at": otp_data["expires_at"],
                "attempts": otp_data["attempts"],
                "max_attempts": self.max_attempts,
                "is_expired": is_expired,
                "remaining_attempts": self.max_attempts - otp_data["attempts"]
            }
            
        except Exception as e:
            logger.error(f"Error getting OTP status for {email}: {e}")
            return {
                "has_active_otp": False,
                "message": f"Error getting OTP status: {str(e)}"
            }
