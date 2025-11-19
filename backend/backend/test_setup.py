#!/usr/bin/env python3
"""
Test script to verify the backend setup is working correctly
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test if all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from app.core.config import settings
        print("✅ Configuration imported successfully")
    except Exception as e:
        print(f"❌ Configuration import failed: {e}")
        return False
    
    try:
        from app.main import app
        print("✅ FastAPI app imported successfully")
    except Exception as e:
        print(f"❌ FastAPI app import failed: {e}")
        return False
    
    try:
        from app.core.database import get_supabase
        print("✅ Database module imported successfully")
    except Exception as e:
        print(f"❌ Database module import failed: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration values"""
    print("\n🔧 Testing configuration...")
    
    try:
        from app.core.config import settings
        
        print(f"App Name: {settings.APP_NAME}")
        print(f"Version: {settings.VERSION}")
        print(f"Debug: {settings.DEBUG}")
        print(f"Frontend URL: {settings.FRONTEND_URL}")
        print(f"Backend URL: {settings.BACKEND_URL}")
        
        if settings.SUPABASE_URL:
            print("✅ Supabase URL configured")
        else:
            print("⚠️  Supabase URL not configured")
        
        if settings.SECRET_KEY:
            print("✅ Secret key configured")
        else:
            print("⚠️  Secret key not configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI app creation"""
    print("\n🚀 Testing FastAPI app...")
    
    try:
        from app.main import app
        
        # Test if app has the expected attributes
        assert hasattr(app, 'routes'), "App should have routes"
        assert hasattr(app, 'title'), "App should have title"
        
        print(f"✅ FastAPI app created successfully")
        print(f"App title: {app.title}")
        print(f"App version: {app.version}")
        print(f"Number of routes: {len(app.routes)}")
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI app test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🎯 Fundraising Platform Backend - Setup Test")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("FastAPI App Test", test_fastapi_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your backend is ready to run.")
        print("💡 Run 'python start_dev.py' to start the server")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("💡 Run 'python setup.py' for initial configuration")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
