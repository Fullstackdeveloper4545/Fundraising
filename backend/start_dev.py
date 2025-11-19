#!/usr/bin/env python3
"""
Development startup script for the Fundraising Platform Backend
This script starts the server with proper error handling
"""

import sys
import os
import logging
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def check_configuration():
    """Check if basic configuration is available"""
    try:
        from app.core.config import settings
        
        # Check if Supabase is configured
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            print("⚠️  Supabase not configured. Some features will not work.")
            print("📝 Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
            print("🔗 Get credentials from: https://supabase.com")
            return False
        
        if not settings.SECRET_KEY:
            print("⚠️  SECRET_KEY not configured. Using default (not recommended for production)")
            return False
        
        print("✅ Configuration looks good!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def start_server():
    """Start the development server"""
    try:
        import uvicorn
        from app.main import app
        
        print("🚀 Starting Fundraising Platform Backend...")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("🔍 Health Check: http://localhost:8000/health")
        print("=" * 50)
        
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("🎯 Fundraising Platform Backend")
    print("=" * 50)
    
    # Check configuration
    config_ok = check_configuration()
    
    if not config_ok:
        print("\n⚠️  Starting with limited functionality...")
        print("💡 Run 'python setup.py' for initial configuration")
    
    print("\n🚀 Starting server...")
    start_server()

if __name__ == "__main__":
    main()
