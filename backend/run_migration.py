#!/usr/bin/env python3
"""
Database migration script to add referral_count column and pending_approval status
Run this script to update your Supabase database
"""

import os
import sys
from supabase import create_client, Client

def run_migration():
    # Get Supabase credentials from environment
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables are required")
        print("Please set these in your .env file or environment")
        sys.exit(1)
    
    try:
        # Create Supabase client
        supabase: Client = create_client(url, key)
        
        print("Running database migration...")
        
        # Add referral_count column
        print("Adding referral_count column...")
        result = supabase.rpc('exec_sql', {
            'sql': 'ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS referral_count INTEGER DEFAULT 0;'
        }).execute()
        print("✓ referral_count column added")
        
        # Update status constraint
        print("Updating status constraint...")
        result = supabase.rpc('exec_sql', {
            'sql': 'ALTER TABLE campaigns DROP CONSTRAINT IF EXISTS campaigns_status_check;'
        }).execute()
        
        result = supabase.rpc('exec_sql', {
            'sql': '''ALTER TABLE campaigns ADD CONSTRAINT campaigns_status_check 
                CHECK (status IN ('draft', 'pending_approval', 'active', 'paused', 'completed', 'cancelled', 'expired'));'''
        }).execute()
        print("✓ status constraint updated")
        
        # Update existing campaigns
        print("Updating existing campaigns...")
        result = supabase.rpc('exec_sql', {
            'sql': 'UPDATE campaigns SET referral_count = 0 WHERE referral_count IS NULL;'
        }).execute()
        print("✓ existing campaigns updated")
        
        print("\n✅ Migration completed successfully!")
        print("Your database now supports the new referral-based campaign approval flow.")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("\nPlease run the SQL commands manually in your Supabase SQL Editor:")
        print("1. ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS referral_count INTEGER DEFAULT 0;")
        print("2. ALTER TABLE campaigns DROP CONSTRAINT IF EXISTS campaigns_status_check;")
        print("3. ALTER TABLE campaigns ADD CONSTRAINT campaigns_status_check CHECK (status IN ('draft', 'pending_approval', 'active', 'paused', 'completed', 'cancelled', 'expired'));")
        print("4. UPDATE campaigns SET referral_count = 0 WHERE referral_count IS NULL;")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
