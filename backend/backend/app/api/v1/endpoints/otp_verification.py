from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
import logging

from app.core.database import get_supabase
from app.core.auth import get_current_user
from app.models.user import User
from app.services.otp_service import OTPService
from app.services.email_service import EmailService
from app.services.email_templates import get_otp_verification_email_html, get_otp_verification_email_text
from app.core.exceptions import ValidationException

router = APIRouter()
logger = logging.getLogger(__name__)


class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerificationRequest(BaseModel):
    email: EmailStr
    otp_code: str

    @validator('otp_code')
    def validate_otp_code(cls, v):
        if not v or len(v) != 6 or not v.isdigit():
            raise ValueError('OTP code must be exactly 6 digits')
        return v


class OTPResendRequest(BaseModel):
    email: EmailStr


class OTPResponse(BaseModel):
    success: bool
    message: str
    email: str
    expires_in_minutes: Optional[int] = None
    remaining_attempts: Optional[int] = None


@router.post("/send-otp", response_model=OTPResponse)
async def send_otp(request: OTPRequest):
    """Send OTP for email verification"""
    try:
        supabase = get_supabase()
        otp_service = OTPService(supabase)
        
        # Check if user exists and is not verified
        user_result = supabase.table("users").select("*").eq("email", request.email.lower()).execute()
        
        if not user_result.data:
            raise ValidationException("User not found")
        
        user_data = user_result.data[0]
        
        if user_data.get("is_verified", False):
            raise ValidationException("Email is already verified")
        
        # Create OTP
        otp_data = await otp_service.create_otp(request.email, "email_verification")
        
        # Send OTP email
        try:
            email_service = EmailService()
            user_name = f"{user_data['first_name']} {user_data['last_name']}"
            
            html_content = get_otp_verification_email_html(user_name, otp_data["otp_code"])
            text_content = get_otp_verification_email_text(user_name, otp_data["otp_code"])
            
            email_sent = await email_service.send_email(
                request.email,
                "🔐 Email Verification Code - Fundraising Platform",
                html_content,
                text_content
            )
            
            if email_sent:
                logger.info(f"OTP verification email sent to {request.email}")
            else:
                logger.warning(f"Failed to send OTP email to {request.email}")
                # Still return success as OTP was created
                
        except Exception as email_error:
            logger.warning(f"Failed to send OTP email to {request.email}: {email_error}")
            # Don't fail OTP creation if email fails
        
        return OTPResponse(
            success=True,
            message="OTP sent successfully. Check your email.",
            email=request.email,
            expires_in_minutes=10
        )
        
    except Exception as e:
        logger.error(f"Error sending OTP: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-otp", response_model=OTPResponse)
async def verify_otp(request: OTPVerificationRequest):
    """Verify OTP for email verification"""
    try:
        supabase = get_supabase()
        otp_service = OTPService(supabase)
        
        # Verify OTP
        is_valid = await otp_service.verify_otp(request.email, request.otp_code, "email_verification")
        
        if is_valid:
            # Update user verification status
            supabase.table("users").update({
                "is_verified": True,
                "updated_at": __import__('datetime').datetime.utcnow().isoformat()
            }).eq("email", request.email.lower()).execute()
            
            logger.info(f"Email verified successfully for {request.email}")
            
            return OTPResponse(
                success=True,
                message="Email verified successfully! You can now log in.",
                email=request.email
            )
        else:
            # Get OTP status for remaining attempts
            otp_status = await otp_service.get_otp_status(request.email, "email_verification")
            
            return OTPResponse(
                success=False,
                message="Invalid OTP code. Please try again.",
                email=request.email,
                remaining_attempts=otp_status.get("remaining_attempts", 0)
            )
            
    except Exception as e:
        logger.error(f"Error verifying OTP: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/resend-otp", response_model=OTPResponse)
async def resend_otp(request: OTPResendRequest):
    """Resend OTP for email verification"""
    try:
        supabase = get_supabase()
        otp_service = OTPService(supabase)
        
        # Check if user exists and is not verified
        user_result = supabase.table("users").select("*").eq("email", request.email.lower()).execute()
        
        if not user_result.data:
            raise ValidationException("User not found")
        
        user_data = user_result.data[0]
        
        if user_data.get("is_verified", False):
            raise ValidationException("Email is already verified")
        
        # Resend OTP
        otp_data = await otp_service.resend_otp(request.email, "email_verification")
        
        # Send OTP email
        try:
            email_service = EmailService()
            user_name = f"{user_data['first_name']} {user_data['last_name']}"
            
            html_content = get_otp_verification_email_html(user_name, otp_data["otp_code"])
            text_content = get_otp_verification_email_text(user_name, otp_data["otp_code"])
            
            email_sent = await email_service.send_email(
                request.email,
                "🔐 New Email Verification Code - Fundraising Platform",
                html_content,
                text_content
            )
            
            if email_sent:
                logger.info(f"OTP resend email sent to {request.email}")
            else:
                logger.warning(f"Failed to resend OTP email to {request.email}")
                
        except Exception as email_error:
            logger.warning(f"Failed to resend OTP email to {request.email}: {email_error}")
        
        return OTPResponse(
            success=True,
            message="New OTP sent successfully. Check your email.",
            email=request.email,
            expires_in_minutes=10
        )
        
    except Exception as e:
        logger.error(f"Error resending OTP: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/otp-status/{email}")
async def get_otp_status(email: str):
    """Get OTP status for an email"""
    try:
        supabase = get_supabase()
        otp_service = OTPService(supabase)
        
        # Check if user exists
        user_result = supabase.table("users").select("is_verified").eq("email", email.lower()).execute()
        
        if not user_result.data:
            raise ValidationException("User not found")
        
        user_data = user_result.data[0]
        
        if user_data.get("is_verified", False):
            return {
                "email": email,
                "is_verified": True,
                "message": "Email is already verified"
            }
        
        # Get OTP status
        otp_status = await otp_service.get_otp_status(email, "email_verification")
        
        return {
            "email": email,
            "is_verified": False,
            "has_active_otp": otp_status.get("has_active_otp", False),
            "expires_at": otp_status.get("expires_at"),
            "remaining_attempts": otp_status.get("remaining_attempts", 0),
            "max_attempts": otp_status.get("max_attempts", 3)
        }
        
    except Exception as e:
        logger.error(f"Error getting OTP status: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/test-otp-public")
async def test_otp_public(request: OTPRequest):
    """Test OTP sending (public - no auth required)"""
    try:
        supabase = get_supabase()
        otp_service = OTPService(supabase)
        
        # Create OTP
        otp_data = await otp_service.create_otp(request.email, "email_verification")
        
        # Send test OTP email
        try:
            email_service = EmailService()
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #4F46E5;">🧪 OTP Test Email</h2>
                    <p>Hello!</p>
                    <p>This is a test OTP email from the Fundraising Platform.</p>
                    <p><strong>Test OTP Code:</strong></p>
                    <div style="text-align: center; margin: 30px 0;">
                        <div style="background-color: #4F46E5; color: white; padding: 20px; border-radius: 10px; font-size: 32px; font-weight: bold; letter-spacing: 5px; display: inline-block;">
                            {otp_data["otp_code"]}
                        </div>
                    </div>
                    <p>This is a test email. The OTP code above is for testing purposes only.</p>
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
                    <p style="color: #6c757d; font-size: 14px;">
                        Best regards,<br>
                        The Fundraising Platform Team
                    </p>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            OTP Test Email
            
            Hello!
            
            This is a test OTP email from the Fundraising Platform.
            
            Test OTP Code: {otp_data["otp_code"]}
            
            This is a test email. The OTP code above is for testing purposes only.
            
            Best regards,
            The Fundraising Platform Team
            """
            
            email_sent = await email_service.send_email(
                request.email,
                "🧪 OTP Test Email - Fundraising Platform",
                html_content,
                text_content
            )
            
            if email_sent:
                logger.info(f"OTP test email sent to {request.email}")
            else:
                logger.warning(f"Failed to send OTP test email to {request.email}")
                
        except Exception as email_error:
            logger.warning(f"Failed to send OTP test email to {request.email}: {email_error}")
        
        return {
            "success": True,
            "message": "OTP test email sent successfully",
            "email": request.email,
            "otp_code": otp_data["otp_code"],
            "expires_at": otp_data["expires_at"]
        }
        
    except Exception as e:
        logger.error(f"Error sending test OTP: {e}")
        raise HTTPException(status_code=400, detail=str(e))
