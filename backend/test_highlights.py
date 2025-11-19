#!/usr/bin/env python3
"""
Test script for student highlights functionality
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin123"  # Default password from schema

def login_as_admin():
    """Login as admin and get token"""
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_create_highlight(token):
    """Test creating a student highlight"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "user_id": 7,
            "achievement": "Olympiad Winner",
            "description": "Scored 99 percentile in olympiad",
            "image_url": "https://example.com/image.jpg"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/highlights/create",
            headers=headers,
            params=params
        )
        
        print(f"Create highlight response: {response.status_code}")
        if response.status_code == 200:
            print("Student highlight created successfully!")
            print(f"Response: {response.json()}")
        else:
            print(f"Failed to create highlight: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error creating highlight: {e}")
        return False

def test_get_highlights():
    """Test getting highlights (no auth required)"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/highlights/current")
        
        print(f"Get highlights response: {response.status_code}")
        if response.status_code == 200:
            print("Successfully retrieved highlights!")
            print(f"Response: {response.json()}")
        else:
            print(f"Failed to get highlights: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error getting highlights: {e}")
        return False

def main():
    print("Testing Student Highlights Functionality")
    print("=" * 50)
    
    # Test 1: Login as admin
    print("\n1. Testing admin login...")
    token = login_as_admin()
    if not token:
        print("Cannot proceed without admin token")
        return False
    
        print("Admin login successful")
    
    # Test 2: Create highlight
    print("\n2. Testing highlight creation...")
    create_success = test_create_highlight(token)
    
    # Test 3: Get highlights
    print("\n3. Testing highlight retrieval...")
    get_success = test_get_highlights()
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Admin Login: {'PASS' if token else 'FAIL'}")
    print(f"Create Highlight: {'PASS' if create_success else 'FAIL'}")
    print(f"Get Highlights: {'PASS' if get_success else 'FAIL'}")
    
    if create_success and get_success:
        print("\nAll tests passed! Student highlights are working.")
        return True
    else:
        print("\nSome tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
