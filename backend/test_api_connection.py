#!/usr/bin/env python3
"""
API Connection Test Script
Tests the basic API endpoints to ensure they're working properly
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
API_V1_URL = f"{API_BASE_URL}/api/v1"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_campaigns_endpoint():
    """Test the campaigns endpoint"""
    print("🔍 Testing campaigns endpoint...")
    try:
        response = requests.get(f"{API_V1_URL}/campaigns", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Campaigns endpoint working: Found {len(data)} campaigns")
            return True
        else:
            print(f"❌ Campaigns endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Campaigns endpoint error: {e}")
        return False

def test_auth_endpoint():
    """Test the auth endpoint structure"""
    print("🔍 Testing auth endpoint structure...")
    try:
        # Test with invalid credentials to check endpoint exists
        response = requests.post(
            f"{API_V1_URL}/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
            timeout=10
        )
        if response.status_code in [400, 401, 422]:  # Expected error codes
            print("✅ Auth endpoint structure is correct")
            return True
        else:
            print(f"❌ Auth endpoint unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Auth endpoint error: {e}")
        return False

def test_admin_endpoint():
    """Test admin endpoint structure"""
    print("🔍 Testing admin endpoint structure...")
    try:
        # Test without token to check endpoint exists
        response = requests.get(f"{API_V1_URL}/admin/stats", timeout=10)
        if response.status_code in [401, 403]:  # Expected unauthorized
            print("✅ Admin endpoint structure is correct")
            return True
        else:
            print(f"❌ Admin endpoint unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Admin endpoint error: {e}")
        return False

def test_campaign_creation_structure():
    """Test campaign creation endpoint structure"""
    print("🔍 Testing campaign creation endpoint structure...")
    try:
        # Test without token to check endpoint exists
        response = requests.post(
            f"{API_V1_URL}/campaigns/",
            json={
                "title": "Test Campaign",
                "description": "Test Description",
                "goal_amount": 1000,
                "duration_months": "3"
            },
            timeout=10
        )
        if response.status_code in [401, 403]:  # Expected unauthorized
            print("✅ Campaign creation endpoint structure is correct")
            return True
        else:
            print(f"❌ Campaign creation endpoint unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Campaign creation endpoint error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 Starting API Connection Tests")
    print("=" * 50)
    
    tests = [
        test_health_check,
        test_campaigns_endpoint,
        test_auth_endpoint,
        test_admin_endpoint,
        test_campaign_creation_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All API tests passed! The backend is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the backend server.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
