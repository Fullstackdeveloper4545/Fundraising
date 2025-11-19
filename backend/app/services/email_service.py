import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email to recipient"""
        try:
            # Check if email is configured
            if not all([self.smtp_host, self.smtp_username, self.smtp_password]):
                logger.warning(f"Email not configured, logging email instead: {subject} to {to_email}")
                self._log_email_content(to_email, subject, html_content, text_content)
                return True  # Return True for development
            
            # Validate email address
            if not self._is_valid_email(to_email):
                logger.error(f"Invalid email address: {to_email}")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            
            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                        server.starttls()
                        server.login(self.smtp_username, self.smtp_password)
                        server.send_message(msg)
                    
                    logger.info(f"Email sent successfully to {to_email}")
                    return True
                    
                except smtplib.SMTPException as e:
                    logger.warning(f"SMTP error on attempt {attempt + 1}: {e}")
                    if attempt == max_retries - 1:
                        raise
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                    if attempt == max_retries - 1:
                        raise
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            # Log email content for debugging
            self._log_email_content(to_email, subject, html_content, text_content)
            return False

    def _is_valid_email(self, email: str) -> bool:
        """Validate email address format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def _log_email_content(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None):
        """Log email content for debugging when email is not configured"""
        logger.info("=" * 50)
        logger.info(f"EMAIL DEBUG - To: {to_email}")
        logger.info(f"EMAIL DEBUG - Subject: {subject}")
        logger.info("EMAIL DEBUG - Content:")
        if text_content:
            logger.info(f"TEXT: {text_content}")
        logger.info(f"HTML: {html_content}")
        logger.info("=" * 50)

    async def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Send welcome email to new user"""
        subject = "Welcome to Fundraising Platform!"
        
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to Fundraising Platform, {user_name}!</h2>
            <p>Thank you for joining our community of student fundraisers.</p>
            <p>You can now:</p>
            <ul>
                <li>Create your first campaign</li>
                <li>Refer 5 friends to meet the requirement</li>
                <li>Start raising funds for your goals</li>
            </ul>
            <p>Get started by creating your campaign today!</p>
            <p>Best regards,<br>The Fundraising Platform Team</p>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_content)

    async def send_password_reset_email(self, user_email: str, user_name: str, reset_token: str) -> bool:
        """Send password reset email with user name"""
        subject = "Reset your password - Fundraising Platform"
        
        html_content = f"""
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
        
        text_content = f"""
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
        
        return await self.send_email(user_email, subject, html_content, text_content)

    async def send_partnership_request(
        self,
        company_name: str,
        contact_name: str,
        contact_email: str,
        message: str
    ) -> bool:
        """Send partnership request notification to fundraising team"""
        subject = f"New Partnership Request from {company_name}"
        
        # Prepare message section for HTML
        message_html = ""
        if message:
            message_html = f'<div style="background-color: white; padding: 15px; border-radius: 8px; margin: 20px 0;"><h3 style="margin-top: 0; color: #333;">Message</h3><p style="white-space: pre-wrap;">{message}</p></div>'
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                <h2 style="color: #4F46E5;">New Partnership Request</h2>
                <p>A new organization has requested to partner with our fundraising platform.</p>
                
                <div style="background-color: white; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #4F46E5;">
                    <h3 style="margin-top: 0; color: #333;">Organization Details</h3>
                    <p><strong>Company/Organization:</strong> {company_name}</p>
                    <p><strong>Contact Person:</strong> {contact_name}</p>
                    <p><strong>Email:</strong> {contact_email}</p>
                </div>
                
                {message_html}
                
                <div style="background-color: #e9ecef; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #333;">Next Steps</h3>
                    <ul>
                        <li>Review the partnership request</li>
                        <li>Contact {contact_name} at {contact_email}</li>
                        <li>Discuss partnership terms and benefits</li>
                        <li>Add organization to partner list if approved</li>
                    </ul>
                </div>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
                <p style="color: #6c757d; font-size: 14px;">
                    This email was sent from the Fundraising Platform partnership request form.<br>
                    <a href="{settings.FRONTEND_URL}">{settings.FRONTEND_URL}</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        # Prepare message section for text
        message_text = f"Message:\n{message}\n" if message else ""
        
        text_content = f"""
        New Partnership Request
        
        A new organization has requested to partner with our fundraising platform.
        
        Organization Details:
        Company/Organization: {company_name}
        Contact Person: {contact_name}
        Email: {contact_email}
        
        {message_text}
        Next Steps:
        - Review the partnership request
        - Contact {contact_name} at {contact_email}
        - Discuss partnership terms and benefits
        - Add organization to partner list if approved
        
        This email was sent from the Fundraising Platform partnership request form.
        {settings.FRONTEND_URL}
        """
        
        # Send to fundraising2121@gmail.com
        return await self.send_email("fundraising2121@gmail.com", subject, html_content, text_content)

    async def send_referral_email(
        self,
        invited_email: str,
        inviter_name: str,
        campaign_title: str,
        referral_token: str
    ) -> bool:
        """Send referral invitation email"""
        subject = f"{inviter_name} invited you to support their campaign!"
        
        html_content = f"""
        <html>
        <body>
            <h2>You're invited to support a campaign!</h2>
            <p>{inviter_name} has invited you to support their campaign: <strong>{campaign_title}</strong></p>
            <p>Click the link below to view and support their campaign:</p>
            <p><a href="{settings.FRONTEND_URL}/campaign/referral/{referral_token}" 
               style="background-color: #4F46E5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
               View Campaign
            </a></p>
            <p>Thank you for supporting student fundraisers!</p>
            <p>Best regards,<br>The Fundraising Platform Team</p>
        </body>
        </html>
        """
        
        return await self.send_email(invited_email, subject, html_content)

    async def send_donation_confirmation(
        self,
        donor_email: str,
        donor_name: str,
        amount: float,
        campaign_title: str
    ) -> bool:
        """Send donation confirmation email"""
        subject = "Thank you for your donation!"
        
        html_content = f"""
        <html>
        <body>
            <h2>Thank you for your donation, {donor_name}!</h2>
            <p>Your donation of <strong>${amount:.2f}</strong> to <strong>{campaign_title}</strong> has been received.</p>
            <p>Your support makes a real difference in helping students achieve their goals.</p>
            <p>A receipt has been generated and is available in your account.</p>
            <p>Thank you for supporting student fundraisers!</p>
            <p>Best regards,<br>The Fundraising Platform Team</p>
        </body>
        </html>
        """
        
        return await self.send_email(donor_email, subject, html_content)

    async def send_campaign_update(
        self,
        supporter_email: str,
        supporter_name: str,
        campaign_title: str,
        update_message: str
    ) -> bool:
        """Send campaign update to supporters"""
        subject = f"Update from {campaign_title}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Campaign Update: {campaign_title}</h2>
            <p>Dear {supporter_name},</p>
            <p>{update_message}</p>
            <p>Thank you for your continued support!</p>
            <p>Best regards,<br>The Fundraising Platform Team</p>
        </body>
        </html>
        """
        
        return await self.send_email(supporter_email, subject, html_content)

    async def send_password_reset(self, user_email: str, reset_token: str) -> bool:
        """Send password reset email"""
        subject = "Reset your password"
        
        html_content = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>You requested to reset your password. Click the link below to reset it:</p>
            <p><a href="{settings.FRONTEND_URL}/reset-password?token={reset_token}" 
               style="background-color: #4F46E5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
               Reset Password
            </a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this, please ignore this email.</p>
            <p>Best regards,<br>The Fundraising Platform Team</p>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_content)

    async def send_password_reset_email(self, user_email: str, user_name: str, reset_token: str) -> bool:
        """Send password reset email with user name"""
        subject = "Reset your password - Fundraising Platform"
        
        html_content = f"""
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
        
        text_content = f"""
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
        
        return await self.send_email(user_email, subject, html_content, text_content)

    async def send_partnership_request(
        self,
        company_name: str,
        contact_name: str,
        contact_email: str,
        message: str
    ) -> bool:
        """Send partnership request notification to fundraising team"""
        subject = f"New Partnership Request from {company_name}"
        
        # Prepare message section for HTML
        message_html = ""
        if message:
            message_html = f'<div style="background-color: white; padding: 15px; border-radius: 8px; margin: 20px 0;"><h3 style="margin-top: 0; color: #333;">Message</h3><p style="white-space: pre-wrap;">{message}</p></div>'
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                <h2 style="color: #4F46E5;">New Partnership Request</h2>
                <p>A new organization has requested to partner with our fundraising platform.</p>
                
                <div style="background-color: white; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #4F46E5;">
                    <h3 style="margin-top: 0; color: #333;">Organization Details</h3>
                    <p><strong>Company/Organization:</strong> {company_name}</p>
                    <p><strong>Contact Person:</strong> {contact_name}</p>
                    <p><strong>Email:</strong> {contact_email}</p>
                </div>
                
                {message_html}
                
                <div style="background-color: #e9ecef; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #333;">Next Steps</h3>
                    <ul>
                        <li>Review the partnership request</li>
                        <li>Contact {contact_name} at {contact_email}</li>
                        <li>Discuss partnership terms and benefits</li>
                        <li>Add organization to partner list if approved</li>
                    </ul>
                </div>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
                <p style="color: #6c757d; font-size: 14px;">
                    This email was sent from the Fundraising Platform partnership request form.<br>
                    <a href="{settings.FRONTEND_URL}">{settings.FRONTEND_URL}</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        # Prepare message section for text
        message_text = f"Message:\n{message}\n" if message else ""
        
        text_content = f"""
        New Partnership Request
        
        A new organization has requested to partner with our fundraising platform.
        
        Organization Details:
        Company/Organization: {company_name}
        Contact Person: {contact_name}
        Email: {contact_email}
        
        {message_text}
        Next Steps:
        - Review the partnership request
        - Contact {contact_name} at {contact_email}
        - Discuss partnership terms and benefits
        - Add organization to partner list if approved
        
        This email was sent from the Fundraising Platform partnership request form.
        {settings.FRONTEND_URL}
        """
        
        # Send to fundraising2121@gmail.com
        return await self.send_email("fundraising2121@gmail.com", subject, html_content, text_content)
