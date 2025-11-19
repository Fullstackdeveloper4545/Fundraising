from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, constr
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_supabase, get_supabase_admin
from app.core.security import verify_password, get_password_hash, create_access_token, verify_token
from app.core.config import settings
from app.core.auth import get_current_user
from app.models.user import User, UserCreate, UserLogin, UserResponse, UserProfile, UserRole
from app.services.user_service import UserService
from app.core.exceptions import AuthenticationException, ValidationException
from app.core.error_handler import handle_validation_error, handle_attribute_error, create_safe_user_response

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)




@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        # Use admin client to bypass RLS for OTP table
        supabase = get_supabase_admin()
        user_service = UserService(supabase)
        
        # Check if user already exists
        existing_user = await user_service.get_user_by_email(user_data.email)
        if existing_user:
            raise ValidationException("User with this email already exists")
        
        # Enforce allowed roles (only student or donor via public register)
        requested_role = getattr(user_data, "role", None)
        if requested_role:
            role_str = requested_role.value if isinstance(requested_role, UserRole) else str(requested_role).lower()
            if role_str not in ("student", "donor"):
                raise ValidationException("Invalid role for public registration")

        # Create new user
        user = await user_service.create_user(user_data)
        
        # Send OTP for email verification instead of welcome email
        try:
            from app.services.otp_service import OTPService
            from app.services.email_service import EmailService
            from app.services.email_templates import get_otp_verification_email_html, get_otp_verification_email_text
            
            otp_service = OTPService(supabase)
            email_service = EmailService()
            
            # Create OTP
            otp_data = await otp_service.create_otp(user.email, "email_verification")
            
            # Send OTP email
            user_name = f"{user.first_name} {user.last_name}"
            html_content = get_otp_verification_email_html(user_name, otp_data["otp_code"])
            text_content = get_otp_verification_email_text(user_name, otp_data["otp_code"])
            
            email_sent = await email_service.send_email(
                user.email,
                "🔐 Email Verification Code - Fundraising Platform",
                html_content,
                text_content
            )
            
            if email_sent:
                logger.info(f"OTP verification email sent to {user.email}")
            else:
                logger.warning(f"Failed to send OTP verification email to {user.email}")
                # Still return success as user was created
                
        except Exception as email_error:
            logger.warning(f"Failed to send OTP verification email to {user.email}: {email_error}")
            # Don't fail registration if email fails
        
        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            status=user.status,
            is_verified=user.is_verified,
            created_at=user.created_at
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(login_data: UserLogin):
    """Login user and return access token"""
    try:
        # Use admin client for OTP verify and password update operations
        supabase = get_supabase_admin()
        user_service = UserService(supabase)
        
        # If admin credentials are configured, allow admin-only login via saved creds
        if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD_HASH and login_data.email.lower() == settings.ADMIN_EMAIL.lower():
            # Verify password against stored admin hash
            if not verify_password(login_data.password, settings.ADMIN_PASSWORD_HASH):
                raise AuthenticationException("Invalid email or password")
            # Build a minimal admin user response (ID -1 indicates config admin)
            access_token = create_access_token(data={"sub": "-1"})
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": -1,
                    "email": settings.ADMIN_EMAIL,
                    "first_name": "Admin",
                    "last_name": "User",
                    "role": "admin",
                    "status": "active",
                    "is_verified": True,
                    "created_at": "1970-01-01T00:00:00Z"
                }
            }
        
        # Get user by email (internal model for password verification)
        user_internal = await user_service.get_user_internal_by_email(login_data.email)
        if not user_internal:
            raise AuthenticationException("Invalid email or password")
        
        # Verify password
        if not user_internal.password_hash or not verify_password(login_data.password, user_internal.password_hash):
            raise AuthenticationException("Invalid email or password")
        
        # Check if user is verified
        if not user_internal.is_verified:
            raise AuthenticationException("Please verify your email address before logging in. Check your email for the verification code.")
        
        # Convert to public user for response
        user = user_internal.to_public_user()
        
        # Send login notification email
        try:
            from app.services.email_service import EmailService
            email_service = EmailService()
            user_name = f"{user.first_name} {user.last_name}"
            
            # Create login notification email
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #4F46E5;">🔐 Login Notification</h2>
                    <p>Hello {user_name},</p>
                    <p>You have successfully logged into your Fundraising Platform account.</p>
                    <p><strong>Login Details:</strong></p>
                    <ul>
                        <li>Email: {user.email}</li>
                        <li>Role: {user.role.title()}</li>
                        <li>Time: {__import__('datetime').datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</li>
                    </ul>
                    <p>If this wasn't you, please contact support immediately.</p>
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
            Login Notification
            
            Hello {user_name},
            
            You have successfully logged into your Fundraising Platform account.
            
            Login Details:
            - Email: {user.email}
            - Role: {user.role.title()}
            - Time: {__import__('datetime').datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
            
            If this wasn't you, please contact support immediately.
            
            Best regards,
            The Fundraising Platform Team
            """
            
            await email_service.send_email(
                user.email,
                "🔐 Login Notification - Fundraising Platform",
                html_content,
                text_content
            )
            logger.info(f"Login notification email sent to {user.email}")
        except Exception as email_error:
            logger.warning(f"Failed to send login notification email to {user.email}: {email_error}")
            # Don't fail login if email fails
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": create_safe_user_response(user)
        }
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    try:
        supabase = get_supabase()
        user_service = UserService(supabase)
        
        profile = await user_service.get_user_profile(current_user.id)
        return profile
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-email")
async def verify_email(token: str):
    """Verify user email with token"""
    try:
        supabase = get_supabase()
        user_service = UserService(supabase)
        
        result = await user_service.verify_email(token)
        return {"message": "Email verified successfully"}
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest):
    """Send password reset email"""
    try:
        supabase = get_supabase()
        user_service = UserService(supabase)
        
        result = await user_service.send_password_reset(payload.email)
        return {"message": "Password reset email sent"}
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: constr(min_length=8)


@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest):
    """Reset password with token"""
    try:
        supabase = get_supabase()
        user_service = UserService(supabase)
        
        result = await user_service.reset_password(payload.token, payload.new_password)
        
        # Send password reset confirmation email
        if result:
            try:
                from app.services.email_service import EmailService
                email_service = EmailService()
                
                # Get user info for the email
                user_result = supabase.table("users").select("*").eq("reset_token", payload.token).execute()
                if user_result.data:
                    user_data = user_result.data[0]
                    user_name = f"{user_data['first_name']} {user_data['last_name']}"
                    user_email = user_data['email']
                    
                    html_content = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                            <h2 style="color: #4F46E5;">✅ Password Reset Successful</h2>
                            <p>Hello {user_name},</p>
                            <p>Your password has been successfully reset for your Fundraising Platform account.</p>
                            <p><strong>Security Details:</strong></p>
                            <ul>
                                <li>Email: {user_email}</li>
                                <li>Reset Time: {__import__('datetime').datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</li>
                                <li>Status: Password successfully changed</li>
                            </ul>
                            <p>If you didn't make this change, please contact support immediately.</p>
                            <p>You can now log in with your new password.</p>
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
                    Password Reset Successful
                    
                    Hello {user_name},
                    
                    Your password has been successfully reset for your Fundraising Platform account.
                    
                    Security Details:
                    - Email: {user_email}
                    - Reset Time: {__import__('datetime').datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
                    - Status: Password successfully changed
                    
                    If you didn't make this change, please contact support immediately.
                    
                    You can now log in with your new password.
                    
                    Best regards,
                    The Fundraising Platform Team
                    """
                    
                    await email_service.send_email(
                        user_email,
                        "✅ Password Reset Successful - Fundraising Platform",
                        html_content,
                        text_content
                    )
                    logger.info(f"Password reset confirmation email sent to {user_email}")
            except Exception as email_error:
                logger.warning(f"Failed to send password reset confirmation email: {email_error}")
                # Don't fail password reset if email fails
        
        return {"message": "Password reset successfully"}
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ==========================
# OTP-BASED PASSWORD RESET
# ==========================

class OTPRequest(BaseModel):
    email: EmailStr


class OTPResetRequest(BaseModel):
    email: EmailStr
    otp_code: constr(min_length=4, max_length=10)
    new_password: constr(min_length=8)


@router.post("/forgot-password-otp")
async def forgot_password_otp(payload: OTPRequest):
    """Send OTP for password reset via email."""
    try:
        supabase = get_supabase()
        from app.services.otp_service import OTPService
        from app.services.email_service import EmailService
        from app.services.email_templates import get_otp_verification_email_html, get_otp_verification_email_text

        otp_service = OTPService(supabase)
        email_service = EmailService()
        user_service = UserService(supabase)

        # Ensure user exists silently (to avoid account enumeration)
        user = await user_service.get_user_by_email(payload.email)
        if not user:
            # Return success regardless
            return {"message": "If the email exists, an OTP has been sent"}

        # Create OTP for password reset
        otp_data = await otp_service.create_otp(payload.email, purpose="password_reset")

        # Send email with OTP
        user_name = f"{user.first_name} {user.last_name}".strip() or "User"
        html_content = get_otp_verification_email_html(user_name, otp_data["otp_code"])  # reuse template
        text_content = get_otp_verification_email_text(user_name, otp_data["otp_code"])  # reuse template

        await email_service.send_email(
            payload.email,
            "🔐 Password Reset Code - Fundraising Platform",
            html_content,
            text_content,
        )
        return {"message": "OTP sent if the email exists"}
    except Exception as e:
        logger.error(f"Forgot password (OTP) error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset-password-otp")
async def reset_password_otp(payload: OTPResetRequest):
    """Reset password using email + OTP code."""
    try:
        supabase = get_supabase()
        from app.services.otp_service import OTPService
        otp_service = OTPService(supabase)
        user_service = UserService(supabase)

        # Verify OTP
        is_valid = await otp_service.verify_otp(payload.email, payload.otp_code, purpose="password_reset")
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")

        # Reset password directly by email
        user_internal = await user_service.get_user_internal_by_email(payload.email)
        if not user_internal:
            # Do not disclose
            return {"message": "Password reset successfully"}

        # Update password
        from app.core.security import get_password_hash
        supabase.table("users").update({
            "password_hash": get_password_hash(payload.new_password),
            "updated_at": __import__('datetime').datetime.utcnow().isoformat()
        }).eq("id", user_internal.id).execute()

        return {"message": "Password reset successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password (OTP) error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp_code: constr(min_length=4, max_length=10)
    purpose: constr(strip_whitespace=True) = "email_verification"


@router.post("/verify-otp")
async def verify_otp(payload: VerifyOTPRequest):
    """Verify an OTP for a given purpose and perform side-effects (e.g., verify email)."""
    try:
        supabase = get_supabase_admin()
        from app.services.otp_service import OTPService
        otp_service = OTPService(supabase)
        user_service = UserService(supabase)

        valid = await otp_service.verify_otp(payload.email, payload.otp_code, purpose=payload.purpose)
        if not valid:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")

        # If verifying email, mark user as verified
        if payload.purpose == "email_verification":
            user = await user_service.get_user_internal_by_email(payload.email)
            if user:
                supabase.table("users").update({
                    "is_verified": True,
                    "updated_at": __import__('datetime').datetime.utcnow().isoformat()
                }).eq("id", user.id).execute()

        return {"message": "OTP verified"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verify OTP error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ==========================
# RESEND VERIFICATION EMAIL
# ==========================

class ResendVerificationRequest(BaseModel):
    email: EmailStr


@router.post("/resend-verification")
async def resend_verification(payload: ResendVerificationRequest):
    """Resend email verification OTP to a user."""
    try:
        supabase = get_supabase_admin()
        from app.services.otp_service import OTPService
        from app.services.email_service import EmailService
        from app.services.email_templates import get_otp_verification_email_html, get_otp_verification_email_text
        from app.services.user_service import UserService

        user_service = UserService(supabase)
        user = await user_service.get_user_internal_by_email(payload.email)
        if not user:
            # Do not leak existence; return success
            return {"message": "If the email exists, a verification code was resent"}

        otp_service = OTPService(supabase)
        otp = await otp_service.resend_otp(payload.email, purpose="email_verification")

        email_service = EmailService()
        user_name = f"{user.first_name} {user.last_name}".strip() or "User"
        html_content = get_otp_verification_email_html(user_name, otp["otp_code"]) 
        text_content = get_otp_verification_email_text(user_name, otp["otp_code"]) 

        await email_service.send_email(
            payload.email,
            "🔐 Email Verification Code - Fundraising Platform",
            html_content,
            text_content,
        )
        return {"message": "Verification code sent"}
    except Exception as e:
        logger.error(f"Resend verification error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
