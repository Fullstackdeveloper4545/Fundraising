#!/usr/bin/env python3
"""
Email Testing Script for Fundraising Platform
This script helps test the email service functionality
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.email_service import EmailService
from app.core.config import settings


async def test_email_service():
    """Test the email service functionality"""
    print("🧪 Testing Email Service")
    print("=" * 50)
    
    # Check configuration
    print("📋 Configuration Check:")
    print(f"SMTP Host: {settings.SMTP_HOST}")
    print(f"SMTP Port: {settings.SMTP_PORT}")
    print(f"SMTP Username: {settings.SMTP_USERNAME}")
    print(f"SMTP Password: {'***' if settings.SMTP_PASSWORD else 'Not set'}")
    print(f"Email From: {settings.EMAIL_FROM}")
    print(f"Frontend URL: {settings.FRONTEND_URL}")
    print()
    
    # Check if email is configured
    if not all([settings.SMTP_HOST, settings.SMTP_USERNAME, settings.SMTP_PASSWORD]):
        print("⚠️  Email not fully configured!")
        print("📝 Please set the following in your .env file:")
        print("   - SMTP_HOST (e.g., smtp.gmail.com)")
        print("   - SMTP_USERNAME (your email)")
        print("   - SMTP_PASSWORD (your app password)")
        print("   - EMAIL_FROM (your email)")
        print()
        print("💡 For Gmail, use an App Password instead of your regular password")
        print("   Go to: Google Account > Security > 2-Step Verification > App passwords")
        print()
    
    # Initialize email service
    try:
        email_service = EmailService()
        print("✅ Email service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize email service: {e}")
        return
    
    # Get test email from user
    test_email = input("📧 Enter test email address: ").strip()
    if not test_email:
        print("❌ No email address provided")
        return
    
    print(f"\n🚀 Sending test email to: {test_email}")
    
    # Test simple email
    try:
        html_content = """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                <h2 style="color: #4F46E5;">🧪 Email Service Test</h2>
                <p>Hello!</p>
                <p>This is a test email from the Fundraising Platform backend.</p>
                <p>If you received this email, the email service is working correctly! ✅</p>
                <p><strong>Test Details:</strong></p>
                <ul>
                    <li>Service: Fundraising Platform Email Service</li>
                    <li>Type: Simple Test Email</li>
                    <li>Status: Working</li>
                </ul>
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
                <p style="color: #6c757d; font-size: 14px;">
                    Best regards,<br>
                    The Fundraising Platform Team
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = """
        Email Service Test
        
        Hello!
        
        This is a test email from the Fundraising Platform backend.
        
        If you received this email, the email service is working correctly! ✅
        
        Test Details:
        - Service: Fundraising Platform Email Service
        - Type: Simple Test Email
        - Status: Working
        
        Best regards,
        The Fundraising Platform Team
        """
        
        success = await email_service.send_email(
            test_email,
            "🧪 Email Service Test - Fundraising Platform",
            html_content,
            text_content
        )
        
        if success:
            print("✅ Test email sent successfully!")
            print("📬 Check your inbox (and spam folder)")
        else:
            print("❌ Failed to send test email")
            print("📝 Check the logs above for error details")
            
    except Exception as e:
        print(f"❌ Error sending test email: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Email Test Complete")


async def test_different_email_types():
    """Test different types of emails"""
    print("\n🧪 Testing Different Email Types")
    print("=" * 50)
    
    email_service = EmailService()
    test_email = input("📧 Enter test email address: ").strip()
    
    if not test_email:
        print("❌ No email address provided")
        return
    
    # Test welcome email
    print("\n1️⃣ Testing Welcome Email...")
    try:
        success = await email_service.send_welcome_email(test_email, "Test User")
        print(f"   {'✅' if success else '❌'} Welcome email: {'Sent' if success else 'Failed'}")
    except Exception as e:
        print(f"   ❌ Welcome email error: {e}")
    
    # Test password reset email
    print("\n2️⃣ Testing Password Reset Email...")
    try:
        success = await email_service.send_password_reset_email(test_email, "Test User", "test_token_12345")
        print(f"   {'✅' if success else '❌'} Password reset email: {'Sent' if success else 'Failed'}")
    except Exception as e:
        print(f"   ❌ Password reset email error: {e}")
    
    # Test referral email
    print("\n3️⃣ Testing Referral Email...")
    try:
        success = await email_service.send_referral_email(test_email, "Test Inviter", "Test Campaign", "test_token_12345")
        print(f"   {'✅' if success else '❌'} Referral email: {'Sent' if success else 'Failed'}")
    except Exception as e:
        print(f"   ❌ Referral email error: {e}")
    
    # Test donation confirmation
    print("\n4️⃣ Testing Donation Confirmation Email...")
    try:
        success = await email_service.send_donation_confirmation(test_email, "Test Donor", 50.00, "Test Campaign")
        print(f"   {'✅' if success else '❌'} Donation confirmation email: {'Sent' if success else 'Failed'}")
    except Exception as e:
        print(f"   ❌ Donation confirmation email error: {e}")
    
    print("\n🎯 All email type tests complete!")


def main():
    """Main function"""
    print("🎯 Fundraising Platform - Email Service Tester")
    print("=" * 50)
    
    while True:
        print("\n📋 Choose an option:")
        print("1. Test simple email")
        print("2. Test all email types")
        print("3. Check configuration only")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            asyncio.run(test_email_service())
        elif choice == "2":
            asyncio.run(test_different_email_types())
        elif choice == "3":
            print("\n📋 Current Configuration:")
            print(f"SMTP Host: {settings.SMTP_HOST}")
            print(f"SMTP Port: {settings.SMTP_PORT}")
            print(f"SMTP Username: {settings.SMTP_USERNAME}")
            print(f"SMTP Password: {'***' if settings.SMTP_PASSWORD else 'Not set'}")
            print(f"Email From: {settings.EMAIL_FROM}")
            print(f"Frontend URL: {settings.FRONTEND_URL}")
            print(f"Backend URL: {settings.BACKEND_URL}")
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    main()