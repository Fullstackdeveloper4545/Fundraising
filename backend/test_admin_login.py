#!/usr/bin/env python3
"""
Test script to verify admin login functionality
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.core.security import verify_password

def test_admin_credentials():
    """Test admin credentials"""
    print("Testing Admin Credentials")
    print("=" * 50)
    
    print(f"ADMIN_EMAIL: {settings.ADMIN_EMAIL}")
    print(f"ADMIN_PASSWORD_HASH: {settings.ADMIN_PASSWORD_HASH}")
    
    if not settings.ADMIN_EMAIL or not settings.ADMIN_PASSWORD_HASH:
        print("Admin credentials not configured")
        return False
    
    # Test with common passwords
    test_passwords = [
        "admin123",
        "Admin@123",
        "admin",
        "password",
        "Admin123",
        "admin@gmail.com",
        "123456",
        "Admin@12345"
    ]
    
    print("\nTesting common passwords:")
    for password in test_passwords:
        if verify_password(password, settings.ADMIN_PASSWORD_HASH):
            print(f"Password found: {password}")
            return True
        else:
            print(f"{password} - No match")
    
    print("\nNo matching password found")
    return False

def test_password_hash():
    """Test password hashing"""
    from app.core.security import get_password_hash
    
    test_password = "Admin@123"
    print(f"\nTesting password hash for: {test_password}")
    
    # Generate new hash
    new_hash = get_password_hash(test_password)
    print(f"New hash: {new_hash}")
    
    # Test verification
    if verify_password(test_password, new_hash):
        print("Password verification works")
    else:
        print("Password verification failed")
    
    # Test with existing hash
    if verify_password(test_password, settings.ADMIN_PASSWORD_HASH):
        print("Existing hash matches test password")
    else:
        print("Existing hash does not match test password")

if __name__ == "__main__":
    test_admin_credentials()
    test_password_hash()
