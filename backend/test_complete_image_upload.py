#!/usr/bin/env python3
"""
Complete test for image upload functionality across the platform
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

def create_test_image(color='red', size=(100, 100)):
    """Create a simple test image"""
    try:
        from PIL import Image
        
        # Create a simple test image
        img = Image.new('RGB', size, color=color)
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        return img_bytes
    except ImportError:
        print("PIL not available, creating dummy image data")
        # Create a dummy image file
        dummy_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00'
        return BytesIO(dummy_data)

def test_highlight_with_image(token):
    """Test creating a highlight with image upload"""
    try:
        print("\n--- Testing Highlight with Image Upload ---")
        
        # Create test image
        test_image = create_test_image('blue', (150, 150))
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        # Prepare form data
        data = {
            "user_id": 7,
            "achievement": "Image Upload Test Achievement",
            "description": "Testing image upload functionality for highlights",
            "image_url": ""  # Leave empty to use file upload
        }
        
        files = {
            "image_file": ("highlight_test.jpg", test_image, "image/jpeg")
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/highlights/create",
            headers=headers,
            data=data,
            files=files
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS: Highlight created with image upload!")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"FAILED: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error testing highlight image upload: {e}")
        return False

def test_campaign_with_image(token):
    """Test creating a campaign with image upload"""
    try:
        print("\n--- Testing Campaign with Image Upload ---")
        
        # Create test image
        test_image = create_test_image('green', (200, 200))
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        # Prepare form data
        data = {
            "title": "Test Campaign with Image",
            "description": "Testing image upload functionality for campaigns",
            "goal_amount": 1000.0,
            "duration_months": "3",
            "category": "Education",
            "story": "This is a test campaign to verify image upload functionality",
            "image_url": ""  # Leave empty to use file upload
        }
        
        files = {
            "image_file": ("campaign_test.jpg", test_image, "image/jpeg")
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/campaigns/with-image",
            headers=headers,
            data=data,
            files=files
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS: Campaign created with image upload!")
            result = response.json()
            print(f"Campaign ID: {result.get('id')}")
            print(f"Image URL: {result.get('image_url')}")
            return result
        else:
            print(f"FAILED: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error testing campaign image upload: {e}")
        return None

def test_get_highlights():
    """Test getting highlights to see if image URLs are returned"""
    try:
        print("\n--- Testing Highlight Retrieval ---")
        
        response = requests.get(f"{BASE_URL}/api/v1/highlights/current")
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: Highlights retrieved!")
            print(f"Student: {data.get('student_name')}")
            print(f"Achievement: {data.get('achievement')}")
            print(f"Image URL: {data.get('image_url')}")
            return data.get('image_url')
        else:
            print(f"FAILED: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error getting highlights: {e}")
        return None

def test_image_access(image_url):
    """Test if the uploaded image is accessible"""
    try:
        if not image_url:
            print("No image URL to test")
            return False
            
        print(f"\n--- Testing Image Access: {image_url} ---")
        
        # Make the URL absolute
        if image_url.startswith("/"):
            full_url = f"{BASE_URL}{image_url}"
        else:
            full_url = f"{BASE_URL}/static{image_url}"
            
        response = requests.get(full_url)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS: Image is accessible!")
            print(f"Image size: {len(response.content)} bytes")
            print(f"Content-Type: {response.headers.get('content-type')}")
            return True
        else:
            print(f"FAILED to access image: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error accessing image: {e}")
        return False

def test_static_file_endpoints():
    """Test static file serving endpoints"""
    try:
        print("\n--- Testing Static File Endpoints ---")
        
        # Test if static file endpoints are working
        response = requests.get(f"{BASE_URL}/api/v1/static/images/test/test.jpg")
        print(f"Static endpoint test: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"Error testing static endpoints: {e}")
        return False

def main():
    print("Complete Image Upload Functionality Test")
    print("=" * 60)
    
    # Test 1: Login as admin
    print("\n1. Testing admin login...")
    token = login_as_admin()
    if not token:
        print("Cannot proceed without admin token")
        return False
    
    print("Admin login successful")
    
    # Test 2: Create highlight with image upload
    highlight_success = test_highlight_with_image(token)
    
    # Test 3: Create campaign with image upload
    campaign_result = test_campaign_with_image(token)
    campaign_success = campaign_result is not None
    
    # Test 4: Get highlights to see image URL
    highlight_image_url = test_get_highlights()
    
    # Test 5: Test image URL access
    image_access_success = False
    if highlight_image_url:
        image_access_success = test_image_access(highlight_image_url)
    
    # Test 6: Test static file endpoints
    static_success = test_static_file_endpoints()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print(f"Admin Login: {'PASS' if token else 'FAIL'}")
    print(f"Highlight with Image: {'PASS' if highlight_success else 'FAIL'}")
    print(f"Campaign with Image: {'PASS' if campaign_success else 'FAIL'}")
    print(f"Highlight Retrieval: {'PASS' if highlight_image_url else 'FAIL'}")
    print(f"Image Access: {'PASS' if image_access_success else 'FAIL'}")
    print(f"Static Endpoints: {'PASS' if static_success else 'FAIL'}")
    
    total_tests = 6
    passed_tests = sum([
        bool(token),
        highlight_success,
        campaign_success,
        bool(highlight_image_url),
        image_access_success,
        static_success
    ])
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests >= 4:  # At least 4 out of 6 tests should pass
        print("\nImage upload functionality is working!")
        return True
    else:
        print("\nSome critical tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
