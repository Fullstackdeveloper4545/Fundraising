#!/usr/bin/env python3
"""
Simple test for highlights GET endpoint
"""

import requests
import json

def test_get_highlights():
    """Test getting highlights"""
    try:
        print("Testing GET /api/v1/highlights/current...")
        response = requests.get("http://localhost:8000/api/v1/highlights/current")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("SUCCESS: Highlights retrieved!")
            data = response.json()
            print(f"Highlight data: {json.dumps(data, indent=2)}")
        else:
            print(f"FAILED: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_weekly_highlights():
    """Test getting weekly highlights"""
    try:
        print("\nTesting GET /api/v1/highlights/weekly...")
        response = requests.get("http://localhost:8000/api/v1/highlights/weekly")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("SUCCESS: Weekly highlights retrieved!")
            data = response.json()
            print(f"Weekly highlights: {json.dumps(data, indent=2)}")
        else:
            print(f"FAILED: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Highlights GET Endpoints")
    print("=" * 40)
    
    current_success = test_get_highlights()
    weekly_success = test_get_weekly_highlights()
    
    print("\n" + "=" * 40)
    print("Results:")
    print(f"Current Highlights: {'PASS' if current_success else 'FAIL'}")
    print(f"Weekly Highlights: {'PASS' if weekly_success else 'FAIL'}")
    
    if current_success or weekly_success:
        print("\nAt least one endpoint is working!")
    else:
        print("\nAll GET endpoints failed.")
