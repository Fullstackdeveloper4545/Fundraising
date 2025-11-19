#!/usr/bin/env python3
"""
Test script to verify authentication fixes
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_user_models():
    """Test user model creation and attribute access"""
    print("🧪 Testing User Models...")
    
    try:
        from app.models.user import User, UserRole, UserStatus
        from app.models.user_internal import UserInternal
        from datetime import datetime
        
        # Test User model
        user = User(
            id=1,
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            role=UserRole.STUDENT,
            status=UserStatus.ACTIVE,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        
        # Test attribute access
        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.role == UserRole.STUDENT
        assert user.status == UserStatus.ACTIVE
        assert user.is_verified == True
        
        print("✅ User model attributes work correctly")
        
        # Test UserInternal model
        user_internal = UserInternal(
            id=1,
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            role=UserRole.STUDENT,
            status=UserStatus.ACTIVE,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        
        # Test conversion to public user
        public_user = user_internal.to_public_user()
        assert public_user.id == 1
        assert public_user.email == "test@example.com"
        assert public_user.password_hash is None  # Should be None for security
        assert public_user.first_name == "John"
        
        print("✅ UserInternal model and conversion work correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ User model test failed: {e}")
        return False

def test_error_handling():
    """Test error handling utilities"""
    print("\n🧪 Testing Error Handling...")
    
    try:
        from app.core.error_handler import safe_get_attr, create_safe_user_response
        
        # Test safe attribute access
        class TestObj:
            def __init__(self):
                self.id = 1
                self.name = "test"
        
        obj = TestObj()
        
        # Test existing attribute
        assert safe_get_attr(obj, "id") == 1
        assert safe_get_attr(obj, "name") == "test"
        
        # Test missing attribute
        assert safe_get_attr(obj, "missing_attr", "default") == "default"
        
        # Test safe user response
        user_response = create_safe_user_response(obj)
        assert user_response["id"] == 1
        assert user_response["name"] == "test"
        
        print("✅ Error handling utilities work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_imports():
    """Test that all modules can be imported without errors"""
    print("\n🧪 Testing Imports...")
    
    try:
        from app.models.user import User, UserCreate, UserLogin, UserResponse, UserProfile
        from app.models.user_internal import UserInternal
        from app.core.error_handler import safe_get_attr, create_safe_user_response
        from app.core.auth import get_current_user
        from app.core.security import verify_password, get_password_hash
        
        print("✅ All imports successful")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🎯 Authentication Fix Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("User Models Test", test_user_models),
        ("Error Handling Test", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All authentication fixes are working!")
        print("💡 You can now test user registration and login")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
