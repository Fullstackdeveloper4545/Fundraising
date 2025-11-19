#!/usr/bin/env python3
"""
Test script for image upload functionality
"""

import requests
import json
import os
from io import BytesIO

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin123"

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

def create_test_image():
    """Create a simple test image"""
    from PIL import Image
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes

def test_image_upload_highlight(token):
    """Test creating a highlight with image upload"""
    try:
        # Create test image
        test_image = create_test_image()
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        # Prepare form data
        data = {
            "user_id": 7,
            "achievement": "Test Achievement with Image",
            "description": "Testing image upload functionality",
            "image_url": ""  # Leave empty to use file upload
        }
        
        files = {
            "image_file": ("test_image.jpg", test_image, "image/jpeg")
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/highlights/create",
            headers=headers,
            data=data,
            files=files
        )
        
        print(f"Create highlight with image response: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS: Highlight created with image upload!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"FAILED: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error testing image upload: {e}")
        return False

def test_get_highlights():
    """Test getting highlights to see if image URLs are returned"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/highlights/current")
        
        print(f"Get highlights response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: Highlights retrieved!")
            print(f"Highlight data: {json.dumps(data, indent=2)}")
            
            # Check if image URL is present
            if "image_url" in data and data["image_url"]:
                print(f"Image URL found: {data['image_url']}")
                return True
            else:
                print("No image URL in response")
                return False
        else:
            print(f"FAILED: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error getting highlights: {e}")
        return False

def test_image_url_access(image_url):
    """Test if the uploaded image is accessible"""
    try:
        if not image_url:
            print("No image URL to test")
            return False
            
        # Make the URL absolute
        if image_url.startswith("/"):
            full_url = f"{BASE_URL}{image_url}"
        else:
            full_url = f"{BASE_URL}/static{image_url}"
            
        response = requests.get(full_url)
        
        print(f"Image access response: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS: Image is accessible!")
            print(f"Image size: {len(response.content)} bytes")
            return True
        else:
            print(f"FAILED to access image: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error accessing image: {e}")
        return False

def main():
    print("Testing Image Upload Functionality")
    print("=" * 50)
    
    # Test 1: Login as admin
    print("\n1. Testing admin login...")
    token = login_as_admin()
    if not token:
        print("Cannot proceed without admin token")
        return False
    
    print("Admin login successful")
    
    # Test 2: Create highlight with image upload
    print("\n2. Testing highlight creation with image upload...")
    upload_success = test_image_upload_highlight(token)
    
    # Test 3: Get highlights to see image URL
    print("\n3. Testing highlight retrieval...")
    get_success = test_get_highlights()
    
    # Test 4: Test image URL access (if we have one)
    print("\n4. Testing image URL access...")
    if get_success:
        # Try to get the current highlight to test image access
        try:
            response = requests.get(f"{BASE_URL}/api/v1/highlights/current")
            if response.status_code == 200:
                data = response.json()
                image_url = data.get("image_url")
                if image_url:
                    test_image_url_access(image_url)
        except:
            pass
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Admin Login: {'PASS' if token else 'FAIL'}")
    print(f"Image Upload: {'PASS' if upload_success else 'FAIL'}")
    print(f"Get Highlights: {'PASS' if get_success else 'FAIL'}")
    
    if upload_success and get_success:
        print("\nAll image upload tests passed!")
        return True
    else:
        print("\nSome tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
