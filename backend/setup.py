#!/usr/bin/env python3
"""
Setup script for the Fundraising Platform Backend
This script helps with initial configuration and setup
"""

import os
import secrets
import shutil
from pathlib import Path

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_urlsafe(32)

def create_env_file():
    """Create .env file from template"""
    env_example = Path("env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return
    
    # Copy template
    shutil.copy(env_example, env_file)
    
    # Generate secret key
    secret_key = generate_secret_key()
    
    # Read and update the file
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Replace placeholder secret key
    content = content.replace('your_secret_key_here_make_it_long_and_random', secret_key)
    
    # Write back
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Created .env file with generated secret key")
    print("📝 Please update the Supabase credentials in .env file")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import supabase
        import uvicorn
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Fundraising Platform Backend...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Create .env file
    create_env_file()
    
    print("\n📋 Next steps:")
    print("1. Update your .env file with Supabase credentials")
    print("2. Set up your Supabase project and run the database schema")
    print("3. Run: python run.py")
    print("\n🔗 Useful links:")
    print("- Supabase: https://supabase.com")
    print("- API docs will be available at: http://localhost:8000/docs")
    print("- Database schema: database/supabase_schema.sql")

if __name__ == "__main__":
    main()
