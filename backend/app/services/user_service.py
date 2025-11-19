from typing import Optional, List
from datetime import datetime, timedelta
import logging
import secrets
import string

from app.models.user import User, UserCreate, UserUpdate, UserProfile, UserRole
from app.models.user_internal import UserInternal
from app.core.security import get_password_hash, generate_secure_token, normalize_password
from app.core.exceptions import NotFoundException, ValidationException
from app.services.email_service import EmailService
from app.services.email_templates import get_password_reset_email_html, get_password_reset_email_text

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, supabase):
        self.supabase = supabase

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        try:
            # Generate referral code
            referral_code = self._generate_referral_code()
            
            # Hash password (ensure it fits bcrypt limits)
            safe_password, truncated = normalize_password(user_data.password)
            if truncated:
                logger.warning("Password exceeded bcrypt limit during registration and was truncated.")
            password_hash = get_password_hash(safe_password)
            
            # Check if referred by someone
            referred_by = None
            if user_data.referral_code:
                referrer = await self.get_user_by_referral_code(user_data.referral_code)
                if referrer:
                    referred_by = referrer.id
            
            # Determine role (default student if not provided)
            role_value = (user_data.role.value if hasattr(user_data, 'role') and user_data.role else 'student')

            # Create user data
            user_dict = {
                "email": user_data.email,
                "password_hash": password_hash,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "phone": user_data.phone,
                "role": role_value,
                "status": "active",
                "is_verified": False,
                "referral_code": referral_code,
                "referred_by": referred_by,
                "referral_count": 0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Insert user into database
            result = self.supabase.table("users").insert(user_dict).execute()
            
            if not result.data:
                raise ValidationException("Failed to create user")
            
            user_data_dict = result.data[0]
            return User(**user_data_dict)
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise ValidationException(f"Failed to create user: {str(e)}")

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            result = self.supabase.table("users").select("*").eq("id", user_id).execute()
            
            if not result.data:
                return None
            
            user_internal = UserInternal(**result.data[0])
            return user_internal.to_public_user()
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            result = self.supabase.table("users").select("*").eq("email", email.lower()).execute()
            
            if not result.data:
                return None
            
            user_internal = UserInternal(**result.data[0])
            return user_internal.to_public_user()
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None

    async def get_user_internal_by_email(self, email: str) -> Optional[UserInternal]:
        """Get internal user by email (includes password_hash for authentication)"""
        try:
            result = self.supabase.table("users").select("*").eq("email", email.lower()).execute()
            
            if not result.data:
                return None
            
            return UserInternal(**result.data[0])
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None

    async def get_user_by_referral_code(self, referral_code: str) -> Optional[User]:
        """Get user by referral code"""
        try:
            result = self.supabase.table("users").select("*").eq("referral_code", referral_code).execute()
            
            if not result.data:
                return None
            
            return User(**result.data[0])
        except Exception as e:
            logger.error(f"Error getting user by referral code: {e}")
            return None

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        try:
            update_dict = {}
            
            if user_data.first_name:
                update_dict["first_name"] = user_data.first_name
            if user_data.last_name:
                update_dict["last_name"] = user_data.last_name
            if user_data.phone:
                update_dict["phone"] = user_data.phone
            if user_data.password:
                safe_password, truncated = normalize_password(user_data.password)
                if truncated:
                    logger.warning("Password exceeded bcrypt limit during update and was truncated.")
                update_dict["password_hash"] = get_password_hash(safe_password)
            
            update_dict["updated_at"] = datetime.utcnow().isoformat()
            
            result = self.supabase.table("users").update(update_dict).eq("id", user_id).execute()
            
            if not result.data:
                return None
            
            return User(**result.data[0])
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return None

    async def get_user_profile(self, user_id: int) -> UserProfile:
        """Get detailed user profile with statistics"""
        try:
            # Get user basic info
            user = await self.get_user_by_id(user_id)
            if not user:
                raise NotFoundException("User not found")
            
            # Get user campaigns for statistics
            campaigns_result = self.supabase.table("campaigns").select("current_amount").eq("user_id", user_id).execute()
            campaigns = campaigns_result.data if campaigns_result.data else []
            
            # Calculate total donations made
            donations_result = self.supabase.table("campaign_payments").select("amount").eq("donor_id", user_id).execute()
            total_donations = sum(float(payment["amount"]) for payment in donations_result.data) if donations_result.data else 0.0
            
            # Calculate total raised from campaigns
            total_raised = sum(float(campaign["current_amount"]) for campaign in campaigns)
            
            return UserProfile(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone,
                role=user.role,
                status=user.status,
                is_verified=user.is_verified,
                referral_code=user.referral_code,
                referral_count=user.referral_count,
                created_at=user.created_at,
                total_donations=total_donations,
                total_raised=total_raised
            )
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            raise NotFoundException("Failed to get user profile")

    async def verify_email(self, token: str) -> bool:
        """Verify user email with token"""
        try:
            # In a real implementation, you would validate the token
            # and update the user's verification status
            result = self.supabase.table("users").update({
                "is_verified": True,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("verification_token", token).execute()
            
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            return False

    async def send_password_reset(self, email: str) -> bool:
        """Send password reset email"""
        try:
            user = await self.get_user_by_email(email)
            if not user:
                logger.warning(f"Password reset requested for non-existent email: {email}")
                return False
            
            # Generate reset token
            reset_token = generate_secure_token(32)
            
            # Store reset token with expiration
            self.supabase.table("users").update({
                "reset_token": reset_token,
                "reset_token_expires": (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }).eq("id", user.id).execute()
            
            # Send password reset email
            email_service = EmailService()
            user_name = f"{user.first_name} {user.last_name}"
            subject = "Reset your password - Fundraising Platform"
            html_content = get_password_reset_email_html(user_name, reset_token)
            text_content = get_password_reset_email_text(user_name, reset_token)
            
            email_sent = await email_service.send_email(
                to_email=email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if email_sent:
                logger.info(f"Password reset email sent to {email}")
            else:
                logger.warning(f"Failed to send password reset email to {email}")
                # Still return True as the token was generated and stored
                logger.info(f"Password reset token for {email}: {reset_token}")
            
            return True
        except Exception as e:
            logger.error(f"Error sending password reset: {e}")
            return False

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password with token"""
        try:
            # Find user by reset token
            result = self.supabase.table("users").select("*").eq("reset_token", token).execute()
            
            if not result.data:
                return False
            
            user_data = result.data[0]
            
            # Check if token is expired
            if user_data.get("reset_token_expires") and datetime.fromisoformat(user_data["reset_token_expires"]) < datetime.utcnow():
                return False
            
            # Update password and clear reset token
            self.supabase.table("users").update({
                "password_hash": get_password_hash(new_password),
                "reset_token": None,
                "reset_token_expires": None,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user_data["id"]).execute()
            
            return True
        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            return False

    def _generate_referral_code(self) -> str:
        """Generate a unique referral code"""
        while True:
            code = generate_secure_token(8)
            # Check if code already exists
            result = self.supabase.table("users").select("id").eq("referral_code", code).execute()
            if not result.data:
                return code
