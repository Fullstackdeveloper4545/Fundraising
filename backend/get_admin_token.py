#!/usr/bin/env python3
"""
Script to get an admin token for testing email endpoints
"""

import sys
import os
import requests
import json
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings


def get_admin_token():
    """Get admin token using configured admin credentials"""
    try:
        if not settings.ADMIN_EMAIL or not settings.ADMIN_PASSWORD_HASH:
            print("❌ Admin credentials not configured in .env file")
            print("📝 Please set ADMIN_EMAIL and ADMIN_PASSWORD_HASH in your .env file")
            return None
        
        # For now, we'll use a simple approach
        # In production, you'd want to hash the password properly
        print("⚠️  Note: This script assumes you have admin credentials configured")
        print("💡 For testing, you can use the public endpoints instead:")
        print("   - POST /api/v1/email-test/test-public")
        print("   - POST /api/v1/email-test/test-simple-public")
        print("   - GET /api/v1/email-test/status-public")
        print("   - GET /api/v1/email-test/config-public")
        
        return None
        
    except Exception as e:
        print(f"❌ Error getting admin token: {e}")
        return None


def test_public_endpoints():
    """Test the public email endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Public Email Endpoints")
    print("=" * 50)
    
    # Test status endpoint
    try:
        print("1️⃣ Testing status endpoint...")
        response = requests.get(f"{base_url}/api/v1/email-test/status-public")
        if response.status_code == 200:
            data = response.json()
            print("✅ Status endpoint working")
            print(f"   Email configured: {data['smtp_configured']}")
            print(f"   Service status: {data['email_service_status']}")
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
    
    # Test config endpoint
    try:
        print("\n2️⃣ Testing config endpoint...")
        response = requests.get(f"{base_url}/api/v1/email-test/config-public")
        if response.status_code == 200:
            data = response.json()
            print("✅ Config endpoint working")
            print(f"   SMTP Host: {data['smtp_host']}")
            print(f"   SMTP Username: {data['smtp_username']}")
            print(f"   Password configured: {data['smtp_password_configured']}")
        else:
            print(f"❌ Config endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Config endpoint error: {e}")
    
    # Test simple email endpoint
    test_email = input("\n📧 Enter test email address (or press Enter to skip): ").strip()
    if test_email:
        try:
            print(f"\n3️⃣ Testing simple email to {test_email}...")
            response = requests.post(
                f"{base_url}/api/v1/email-test/test-simple-public",
                json={"to_email": test_email}
            )
            if response.status_code == 200:
                data = response.json()
                print("✅ Simple email test completed")
                print(f"   Success: {data['success']}")
                print(f"   Message: {data['message']}")
                print(f"   Email configured: {data['email_configured']}")
            else:
                print(f"❌ Simple email test failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Simple email test error: {e}")


def main():
    """Main function"""
    print("🎯 Fundraising Platform - Email Testing Helper")
    print("=" * 50)
    
    print("📋 Available options:")
    print("1. Test public email endpoints (no auth required)")
    print("2. Get admin token info")
    print("3. Show endpoint URLs")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        test_public_endpoints()
    elif choice == "2":
        get_admin_token()
    elif choice == "3":
        print("\n📋 Public Email Test Endpoints:")
        print("=" * 50)
        print("GET  /api/v1/email-test/status-public")
        print("GET  /api/v1/email-test/config-public")
        print("POST /api/v1/email-test/test-simple-public")
        print("POST /api/v1/email-test/test-public")
        print("\n📋 Admin Email Test Endpoints (require auth):")
        print("=" * 50)
        print("GET  /api/v1/email-test/status")
        print("GET  /api/v1/email-test/config")
        print("POST /api/v1/email-test/test-simple")
        print("POST /api/v1/email-test/test")
        print("\n💡 Use the public endpoints for testing without authentication!")
    else:
        print("❌ Invalid choice. Please enter 1-3.")


if __name__ == "__main__":
    main()
