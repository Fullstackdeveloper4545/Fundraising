#!/usr/bin/env python3
"""
Admin Setup Script for Fundraising Platform
This script helps you set up admin credentials for the platform
"""

import os
import sys
import getpass
from pathlib import Path
from passlib.context import CryptContext

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def get_password_hash(password: str) -> str:
    """Generate password hash using bcrypt"""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

def setup_admin_credentials():
    """Interactive setup for admin credentials"""
    print("🔐 Admin Credentials Setup")
    print("=" * 50)
    
    # Get admin email
    while True:
        admin_email = input("Enter admin email address: ").strip()
        if "@" in admin_email and "." in admin_email:
            break
        print("❌ Please enter a valid email address")
    
    # Get admin password
    while True:
        admin_password = getpass.getpass("Enter admin password: ")
        if len(admin_password) >= 8:
            break
        print("❌ Password must be at least 8 characters long")
    
    # Confirm password
    while True:
        confirm_password = getpass.getpass("Confirm admin password: ")
        if admin_password == confirm_password:
            break
        print("❌ Passwords do not match")
    
    # Generate password hash
    password_hash = get_password_hash(admin_password)
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    env_content = []
    
    if env_file.exists():
        with open(env_file, "r") as f:
            env_content = f.readlines()
    
    # Update or add admin credentials
    admin_email_set = False
    admin_password_set = False
    
    for i, line in enumerate(env_content):
        if line.startswith("ADMIN_EMAIL="):
            env_content[i] = f"ADMIN_EMAIL={admin_email}\n"
            admin_email_set = True
        elif line.startswith("ADMIN_PASSWORD_HASH="):
            env_content[i] = f"ADMIN_PASSWORD_HASH={password_hash}\n"
            admin_password_set = True
    
    # Add new lines if not found
    if not admin_email_set:
        env_content.append(f"ADMIN_EMAIL={admin_email}\n")
    if not admin_password_set:
        env_content.append(f"ADMIN_PASSWORD_HASH={password_hash}\n")
    
    # Write back to .env file
    with open(env_file, "w") as f:
        f.writelines(env_content)
    
    print("\n✅ Admin credentials configured successfully!")
    print(f"📧 Admin Email: {admin_email}")
    print("🔑 Password hash has been generated and stored securely")
    print("\n📝 Next steps:")
    print("1. Start your backend server: python start_dev.py")
    print("2. Visit http://localhost:3000/admin/login")
    print("3. Login with your admin credentials")
    print("\n⚠️  Keep your admin credentials secure!")

def main():
    """Main function"""
    print("🎯 Fundraising Platform - Admin Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app").exists():
        print("❌ Please run this script from the backend directory")
        sys.exit(1)
    
    try:
        setup_admin_credentials()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
