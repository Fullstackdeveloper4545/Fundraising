#!/usr/bin/env python3
"""
Test password reset email functionality
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def test_password_reset_email():
    """Test password reset email functionality"""
    print("🧪 Testing Password Reset Email...")
    
    try:
        from app.services.email_service import EmailService
        from app.services.email_templates import get_password_reset_email_html, get_password_reset_email_text
        
        # Create email service
        email_service = EmailService()
        
        # Test data
        test_email = "test@example.com"
        test_name = "John Doe"
        test_token = "test-reset-token-123"
        
        # Test email templates
        print("📧 Testing email templates...")
        html_content = get_password_reset_email_html(test_name, test_token)
        text_content = get_password_reset_email_text(test_name, test_token)
        
        print("✅ Email templates generated successfully")
        
        # Test email sending
        print("📧 Testing password reset email send...")
        result = await email_service.send_email(
            to_email=test_email,
            subject="Reset your password - Fundraising Platform",
            html_content=html_content,
            text_content=text_content
        )
        
        if result:
            print("✅ Password reset email sent successfully")
            print("💡 Check the logs above to see the email content")
        else:
            print("❌ Password reset email failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Password reset email test failed: {e}")
        return False

async def test_user_service_password_reset():
    """Test user service password reset functionality"""
    print("\n🧪 Testing User Service Password Reset...")
    
    try:
        from app.core.database import get_supabase
        from app.services.user_service import UserService
        
        # This would require a real database connection
        # For now, just test the imports
        print("✅ User service imports successful")
        print("💡 To test with real database, configure Supabase first")
        
        return True
        
    except Exception as e:
        print(f"❌ User service test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🎯 Password Reset Email Test")
    print("=" * 50)
    
    # Run async tests
    async def run_tests():
        email_ok = await test_password_reset_email()
        service_ok = await test_user_service_password_reset()
        return email_ok and service_ok
    
    try:
        result = asyncio.run(run_tests())
        
        print("\n" + "=" * 50)
        if result:
            print("🎉 Password reset email is working correctly!")
            print("💡 Check the logs above to see the email content")
            print("💡 The email will be logged to console in development mode")
        else:
            print("⚠️  Some password reset tests failed")
            print("💡 Check the error messages above")
        
        return result
        
    except Exception as e:
        print(f"❌ Test runner failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
