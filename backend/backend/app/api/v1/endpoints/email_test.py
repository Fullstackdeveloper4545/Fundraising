from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

from app.core.auth import get_current_user
from app.models.user import User
from app.services.email_service import EmailService
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


class TestEmailRequest(BaseModel):
    to_email: EmailStr
    subject: Optional[str] = "Test Email from Fundraising Platform"
    test_type: Optional[str] = "simple"  # simple, welcome, password_reset, referral, donation, campaign_update


class EmailConfigResponse(BaseModel):
    smtp_host: Optional[str]
    smtp_port: Optional[int]
    smtp_username: Optional[str]
    smtp_password_configured: bool
    email_from: Optional[str]
    frontend_url: str
    backend_url: str


@router.get("/config", response_model=EmailConfigResponse)
async def get_email_config(current_user: User = Depends(get_current_user)):
    """Get email configuration status (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return EmailConfigResponse(
        smtp_host=settings.SMTP_HOST,
        smtp_port=settings.SMTP_PORT,
        smtp_username=settings.SMTP_USERNAME,
        smtp_password_configured=bool(settings.SMTP_PASSWORD),
        email_from=settings.EMAIL_FROM,
        frontend_url=settings.FRONTEND_URL,
        backend_url=settings.BACKEND_URL
    )


@router.get("/config-public", response_model=EmailConfigResponse)
async def get_email_config_public():
    """Get email configuration status (public - no auth required)"""
    return EmailConfigResponse(
        smtp_host=settings.SMTP_HOST,
        smtp_port=settings.SMTP_PORT,
        smtp_username=settings.SMTP_USERNAME,
        smtp_password_configured=bool(settings.SMTP_PASSWORD),
        email_from=settings.EMAIL_FROM,
        frontend_url=settings.FRONTEND_URL,
        backend_url=settings.BACKEND_URL
    )


@router.post("/test")
async def test_email_send(
    request: TestEmailRequest,
    current_user: User = Depends(get_current_user)
):
    """Test email sending functionality (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        email_service = EmailService()
        
        # Generate test content based on type
        if request.test_type == "simple":
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #4F46E5;">🧪 Email Test - Fundraising Platform</h2>
                    <p>Hello!</p>
                    <p>This is a test email from the Fundraising Platform backend.</p>
                    <p><strong>Test Details:</strong></p>
                    <ul>
                        <li>Sent to: {request.to_email}</li>
                        <li>Test Type: {request.test_type}</li>
                        <li>Subject: {request.subject}</li>
                        <li>Timestamp: {__import__('datetime').datetime.utcnow().isoformat()}</li>
                    </ul>
                    <p>If you received this email, the email service is working correctly! ✅</p>
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
            Email Test - Fundraising Platform
            
            Hello!
            
            This is a test email from the Fundraising Platform backend.
            
            Test Details:
            - Sent to: {request.to_email}
            - Test Type: {request.test_type}
            - Subject: {request.subject}
            - Timestamp: {__import__('datetime').datetime.utcnow().isoformat()}
            
            If you received this email, the email service is working correctly! ✅
            
            Best regards,
            The Fundraising Platform Team
            """
            
        elif request.test_type == "welcome":
            success = await email_service.send_welcome_email(
                request.to_email, 
                "Test User"
            )
            return {
                "success": success,
                "message": "Welcome email test completed",
                "test_type": request.test_type,
                "to_email": request.to_email
            }
            
        elif request.test_type == "password_reset":
            reset_token = "test_token_12345"
            success = await email_service.send_password_reset_email(
                request.to_email,
                "Test User",
                reset_token
            )
            return {
                "success": success,
                "message": "Password reset email test completed",
                "test_type": request.test_type,
                "to_email": request.to_email,
                "reset_token": reset_token
            }
            
        elif request.test_type == "referral":
            success = await email_service.send_referral_email(
                request.to_email,
                "Test Inviter",
                "Test Campaign Title",
                "test_referral_token_12345"
            )
            return {
                "success": success,
                "message": "Referral email test completed",
                "test_type": request.test_type,
                "to_email": request.to_email
            }
            
        elif request.test_type == "donation":
            success = await email_service.send_donation_confirmation(
                request.to_email,
                "Test Donor",
                50.00,
                "Test Campaign"
            )
            return {
                "success": success,
                "message": "Donation confirmation email test completed",
                "test_type": request.test_type,
                "to_email": request.to_email
            }
            
        elif request.test_type == "campaign_update":
            success = await email_service.send_campaign_update(
                request.to_email,
                "Test Supporter",
                "Test Campaign",
                "This is a test campaign update message."
            )
            return {
                "success": success,
                "message": "Campaign update email test completed",
                "test_type": request.test_type,
                "to_email": request.to_email
            }
            
        else:
            raise HTTPException(
                status_code=400, 
                detail="Invalid test_type. Use: simple, welcome, password_reset, referral, donation, campaign_update"
            )
        
        # Send the test email
        if request.test_type == "simple":
            success = await email_service.send_email(
                request.to_email,
                request.subject,
                html_content,
                text_content
            )
        
        return {
            "success": success,
            "message": f"Email test completed successfully" if success else "Email test failed",
            "test_type": request.test_type,
            "to_email": request.to_email,
            "subject": request.subject,
            "email_configured": bool(settings.SMTP_HOST and settings.SMTP_USERNAME and settings.SMTP_PASSWORD)
        }
        
    except Exception as e:
        logger.error(f"Email test error: {e}")
        raise HTTPException(status_code=500, detail=f"Email test failed: {str(e)}")


@router.post("/test-public")
async def test_email_send_public(request: TestEmailRequest):
    """Test email sending functionality (public - no auth required)"""
    try:
        email_service = EmailService()
        
        # Generate test content based on type
        if request.test_type == "simple":
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #4F46E5;">🧪 Email Test - Fundraising Platform</h2>
                    <p>Hello!</p>
                    <p>This is a test email from the Fundraising Platform backend.</p>
                    <p><strong>Test Details:</strong></p>
                    <ul>
                        <li>Sent to: {request.to_email}</li>
                        <li>Test Type: {request.test_type}</li>
                        <li>Subject: {request.subject}</li>
                        <li>Timestamp: {__import__('datetime').datetime.utcnow().isoformat()}</li>
                    </ul>
                    <p>If you received this email, the email service is working correctly! ✅</p>
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
            Email Test - Fundraising Platform
            
            Hello!
            
            This is a test email from the Fundraising Platform backend.
            
            Test Details:
            - Sent to: {request.to_email}
            - Test Type: {request.test_type}
            - Subject: {request.subject}
            - Timestamp: {__import__('datetime').datetime.utcnow().isoformat()}
            
            If you received this email, the email service is working correctly! ✅
            
            Best regards,
            The Fundraising Platform Team
            """
            
        elif request.test_type == "welcome":
            success = await email_service.send_welcome_email(
                request.to_email, 
                "Test User"
            )
            return {
                "success": success,
                "message": "Welcome email test completed",
                "test_type": request.test_type,
                "to_email": request.to_email
            }
            
        elif request.test_type == "password_reset":
            reset_token = "test_token_12345"
            success = await email_service.send_password_reset_email(
                request.to_email,
                "Test User",
                reset_token
            )
            return {
                "success": success,
                "message": "Password reset email test completed",
                "test_type": request.test_type,
                "to_email": request.to_email,
                "reset_token": reset_token
            }
            
        elif request.test_type == "referral":
            success = await email_service.send_referral_email(
                request.to_email,
                "Test Inviter",
                "Test Campaign Title",
                "test_referral_token_12345"
            )
            return {
                "success": success,
                "message": "Referral email test completed",
                "test_type": request.test_type,
                "to_email": request.to_email
            }
            
        elif request.test_type == "donation":
            success = await email_service.send_donation_confirmation(
                request.to_email,
                "Test Donor",
                50.00,
                "Test Campaign"
            )
            return {
                "success": success,
                "message": "Donation confirmation email test completed",
                "test_type": request.test_type,
                "to_email": request.to_email
            }
            
        elif request.test_type == "campaign_update":
            success = await email_service.send_campaign_update(
                request.to_email,
                "Test Supporter",
                "Test Campaign",
                "This is a test campaign update message."
            )
            return {
                "success": success,
                "message": "Campaign update email test completed",
                "test_type": request.test_type,
                "to_email": request.to_email
            }
            
        else:
            raise HTTPException(
                status_code=400, 
                detail="Invalid test_type. Use: simple, welcome, password_reset, referral, donation, campaign_update"
            )
        
        # Send the test email
        if request.test_type == "simple":
            success = await email_service.send_email(
                request.to_email,
                request.subject,
                html_content,
                text_content
            )
        
        return {
            "success": success,
            "message": f"Email test completed successfully" if success else "Email test failed",
            "test_type": request.test_type,
            "to_email": request.to_email,
            "subject": request.subject,
            "email_configured": bool(settings.SMTP_HOST and settings.SMTP_USERNAME and settings.SMTP_PASSWORD)
        }
        
    except Exception as e:
        logger.error(f"Email test error: {e}")
        raise HTTPException(status_code=500, detail=f"Email test failed: {str(e)}")


@router.post("/test-simple")
async def test_simple_email(
    to_email: EmailStr,
    current_user: User = Depends(get_current_user)
):
    """Quick test for simple email sending (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        email_service = EmailService()
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                <h2 style="color: #4F46E5;">✅ Quick Email Test</h2>
                <p>Hello!</p>
                <p>This is a quick test email from the Fundraising Platform.</p>
                <p>If you see this, the email service is working! 🎉</p>
                <p style="color: #6c757d; font-size: 14px;">
                    Sent at: {__import__('datetime').datetime.utcnow().isoformat()}
                </p>
            </div>
        </body>
        </html>
        """
        
        success = await email_service.send_email(
            to_email,
            "Quick Email Test - Fundraising Platform",
            html_content
        )
        
        return {
            "success": success,
            "message": "Quick email test completed",
            "to_email": to_email,
            "email_configured": bool(settings.SMTP_HOST and settings.SMTP_USERNAME and settings.SMTP_PASSWORD)
        }
        
    except Exception as e:
        logger.error(f"Quick email test error: {e}")
        raise HTTPException(status_code=500, detail=f"Quick email test failed: {str(e)}")


@router.post("/test-simple-public")
async def test_simple_email_public(to_email: EmailStr):
    """Quick test for simple email sending (public - no auth required)"""
    try:
        email_service = EmailService()
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                <h2 style="color: #4F46E5;">✅ Quick Email Test</h2>
                <p>Hello!</p>
                <p>This is a quick test email from the Fundraising Platform.</p>
                <p>If you see this, the email service is working! 🎉</p>
                <p style="color: #6c757d; font-size: 14px;">
                    Sent at: {__import__('datetime').datetime.utcnow().isoformat()}
                </p>
            </div>
        </body>
        </html>
        """
        
        success = await email_service.send_email(
            to_email,
            "Quick Email Test - Fundraising Platform",
            html_content
        )
        
        return {
            "success": success,
            "message": "Quick email test completed",
            "to_email": to_email,
            "email_configured": bool(settings.SMTP_HOST and settings.SMTP_USERNAME and settings.SMTP_PASSWORD)
        }
        
    except Exception as e:
        logger.error(f"Quick email test error: {e}")
        raise HTTPException(status_code=500, detail=f"Quick email test failed: {str(e)}")


@router.get("/status")
async def get_email_status(current_user: User = Depends(get_current_user)):
    """Get email service status and configuration (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check configuration
    smtp_configured = bool(settings.SMTP_HOST and settings.SMTP_USERNAME and settings.SMTP_PASSWORD)
    
    # Test email service initialization
    try:
        email_service = EmailService()
        service_initialized = True
        error_message = None
    except Exception as e:
        service_initialized = False
        error_message = str(e)
    
    return {
        "email_service_status": "configured" if smtp_configured else "not_configured",
        "smtp_configured": smtp_configured,
        "service_initialized": service_initialized,
        "error_message": error_message,
        "configuration": {
            "smtp_host": settings.SMTP_HOST,
            "smtp_port": settings.SMTP_PORT,
            "smtp_username": settings.SMTP_USERNAME,
            "smtp_password_set": bool(settings.SMTP_PASSWORD),
            "email_from": settings.EMAIL_FROM,
            "frontend_url": settings.FRONTEND_URL,
            "backend_url": settings.BACKEND_URL
        },
        "recommendations": [
            "Set SMTP_HOST, SMTP_USERNAME, and SMTP_PASSWORD in .env file" if not smtp_configured else "Email configuration looks good",
            "Use Gmail with App Password for testing" if not smtp_configured else None,
            "Check firewall settings if emails are not being sent" if smtp_configured else None
        ]
    }


@router.get("/status-public")
async def get_email_status_public():
    """Get email service status and configuration (public - no auth required)"""
    # Check configuration
    smtp_configured = bool(settings.SMTP_HOST and settings.SMTP_USERNAME and settings.SMTP_PASSWORD)
    
    # Test email service initialization
    try:
        email_service = EmailService()
        service_initialized = True
        error_message = None
    except Exception as e:
        service_initialized = False
        error_message = str(e)
    
    return {
        "email_service_status": "configured" if smtp_configured else "not_configured",
        "smtp_configured": smtp_configured,
        "service_initialized": service_initialized,
        "error_message": error_message,
        "configuration": {
            "smtp_host": settings.SMTP_HOST,
            "smtp_port": settings.SMTP_PORT,
            "smtp_username": settings.SMTP_USERNAME,
            "smtp_password_set": bool(settings.SMTP_PASSWORD),
            "email_from": settings.EMAIL_FROM,
            "frontend_url": settings.FRONTEND_URL,
            "backend_url": settings.BACKEND_URL
        },
        "recommendations": [
            "Set SMTP_HOST, SMTP_USERNAME, and SMTP_PASSWORD in .env file" if not smtp_configured else "Email configuration looks good",
            "Use Gmail with App Password for testing" if not smtp_configured else None,
            "Check firewall settings if emails are not being sent" if smtp_configured else None
        ]
    }
