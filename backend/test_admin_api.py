#!/usr/bin/env python3
"""
Test script to verify admin login API
"""

import sys
import os
import requests
import json
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_admin_login():
    """Test admin login via API"""
    print("Testing Admin Login API")
    print("=" * 50)
    
    # Test credentials
    admin_email = "admin@gmail.com"
    admin_password = "admin123"
    
    # API endpoint
    url = "http://localhost:8000/api/v1/auth/login"
    
    # Request data
    data = {
        "email": admin_email,
        "password": admin_password
    }
    
    try:
        print(f"Testing login with email: {admin_email}")
        print(f"Password: {admin_password}")
        print(f"URL: {url}")
        
        # Make request
        response = requests.post(url, json=data, timeout=10)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("Login successful!")
            print(f"Access Token: {result.get('access_token', 'N/A')[:50]}...")
            print(f"User Role: {result.get('user', {}).get('role', 'N/A')}")
            print(f"User Email: {result.get('user', {}).get('email', 'N/A')}")
            return True
        else:
            print(f"Login failed: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("Connection error: Is the server running on localhost:8000?")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_wrong_credentials():
    """Test with wrong credentials"""
    print("\nTesting with wrong credentials")
    print("=" * 50)
    
    url = "http://localhost:8000/api/v1/auth/login"
    data = {
        "email": "admin@gmail.com",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_admin_login()
    test_wrong_credentials()
