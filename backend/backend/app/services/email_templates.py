"""
Email templates for the fundraising platform
"""

from app.core.config import settings


def get_otp_verification_email_html(user_name: str, otp_code: str) -> str:
    """Get HTML content for OTP verification email"""
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
            <h2 style="color: #4F46E5;">🔐 Email Verification</h2>
            <p>Hello {user_name},</p>
            <p>Welcome to the Fundraising Platform! Please verify your email address to complete your registration.</p>
            <p><strong>Your verification code is:</strong></p>
            <div style="text-align: center; margin: 30px 0;">
                <div style="background-color: #4F46E5; color: white; padding: 20px; border-radius: 10px; font-size: 32px; font-weight: bold; letter-spacing: 5px; display: inline-block;">
                    {otp_code}
                </div>
            </div>
            <p><strong>Important:</strong></p>
            <ul>
                <li>This code will expire in 10 minutes</li>
                <li>You have 3 attempts to verify</li>
                <li>If you didn't create this account, please ignore this email</li>
                <li>Do not share this code with anyone</li>
            </ul>
            <p>Enter this code in the verification form to complete your registration.</p>
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
            <p style="color: #6c757d; font-size: 14px;">
                Best regards,<br>
                The Fundraising Platform Team<br>
                <a href="{settings.FRONTEND_URL}">{settings.FRONTEND_URL}</a>
            </p>
        </div>
    </body>
    </html>
    """


def get_otp_verification_email_text(user_name: str, otp_code: str) -> str:
    """Get text content for OTP verification email"""
    return f"""
    Email Verification
    
    Hello {user_name},
    
    Welcome to the Fundraising Platform! Please verify your email address to complete your registration.
    
    Your verification code is: {otp_code}
    
    Important:
    - This code will expire in 10 minutes
    - You have 3 attempts to verify
    - If you didn't create this account, please ignore this email
    - Do not share this code with anyone
    
    Enter this code in the verification form to complete your registration.
    
    Best regards,
    The Fundraising Platform Team
    {settings.FRONTEND_URL}
    """


def get_password_reset_email_html(user_name: str, reset_token: str) -> str:
    """Get HTML content for password reset email"""
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
            <h2 style="color: #4F46E5;">Password Reset Request</h2>
            <p>Hello {user_name},</p>
            <p>You requested to reset your password for your Fundraising Platform account.</p>
            <p>Click the button below to reset your password:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{settings.FRONTEND_URL}/reset-password?token={reset_token}" 
                   style="background-color: #4F46E5; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold;">
                   Reset My Password
                </a>
            </div>
            <p><strong>Important:</strong></p>
            <ul>
                <li>This link will expire in 1 hour</li>
                <li>If you didn't request this, please ignore this email</li>
                <li>Your password will remain unchanged until you click the link above</li>
            </ul>
            <p>If the button doesn't work, copy and paste this link into your browser:</p>
            <p style="word-break: break-all; background-color: #e9ecef; padding: 10px; border-radius: 5px;">
                {settings.FRONTEND_URL}/reset-password?token={reset_token}
            </p>
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
            <p style="color: #6c757d; font-size: 14px;">
                Best regards,<br>
                The Fundraising Platform Team<br>
                <a href="{settings.FRONTEND_URL}">{settings.FRONTEND_URL}</a>
            </p>
        </div>
    </body>
    </html>
    """


def get_password_reset_email_text(user_name: str, reset_token: str) -> str:
    """Get text content for password reset email"""
    return f"""
    Password Reset Request
    
    Hello {user_name},
    
    You requested to reset your password for your Fundraising Platform account.
    
    To reset your password, click this link:
    {settings.FRONTEND_URL}/reset-password?token={reset_token}
    
    This link will expire in 1 hour.
    
    If you didn't request this, please ignore this email.
    
    Best regards,
    The Fundraising Platform Team
    """
