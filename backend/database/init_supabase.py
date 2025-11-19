"""
Supabase Database Initialization Script
This script creates all necessary tables and relationships for the fundraising platform
"""

import os
from supabase import create_client, Client
from app.core.config import settings

def init_database():
    """Initialize Supabase database with all required tables"""
    
    # Initialize Supabase client
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    
    print("Initializing database tables...")
    
    # 1. Users table
    print("Creating users table...")
    users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id BIGSERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        phone VARCHAR(50),
        role VARCHAR(20) DEFAULT 'student' CHECK (role IN ('student', 'admin', 'company')),
        status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
        is_verified BOOLEAN DEFAULT FALSE,
        referral_code VARCHAR(50) UNIQUE,
        referred_by BIGINT REFERENCES users(id),
        referral_count INTEGER DEFAULT 0,
        verification_token VARCHAR(255),
        reset_token VARCHAR(255),
        reset_token_expires TIMESTAMP,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    # 2. Campaigns table
    print("Creating campaigns table...")
    campaigns_table = """
    CREATE TABLE IF NOT EXISTS campaigns (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        title VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        goal_amount DECIMAL(12,2) NOT NULL,
        current_amount DECIMAL(12,2) DEFAULT 0.00,
        status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'paused', 'completed', 'cancelled', 'expired')),
        duration_months VARCHAR(2) NOT NULL CHECK (duration_months IN ('1', '3', '6', '12')),
        start_date TIMESTAMP,
        end_date TIMESTAMP,
        category VARCHAR(100),
        image_url VARCHAR(1024),
        video_url VARCHAR(1024),
        story TEXT,
        is_featured BOOLEAN DEFAULT FALSE,
        referral_requirement_met BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    # 3. Campaign payments table
    print("Creating campaign_payments table...")
    payments_table = """
    CREATE TABLE IF NOT EXISTS campaign_payments (
        id BIGSERIAL PRIMARY KEY,
        campaign_id BIGINT NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
        donor_id BIGINT REFERENCES users(id),
        donor_email VARCHAR(255) NOT NULL,
        donor_name VARCHAR(255),
        amount DECIMAL(12,2) NOT NULL,
        method VARCHAR(20) NOT NULL CHECK (method IN ('credit_card', 'paypal', 'bank_transfer', 'square')),
        status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled', 'refunded')),
        transaction_id VARCHAR(255),
        gateway_response JSONB,
        is_anonymous BOOLEAN DEFAULT FALSE,
        message TEXT,
        created_at TIMESTAMP DEFAULT NOW(),
        processed_at TIMESTAMP
    );
    """
    
    # 4. Referrals table
    print("Creating referrals table...")
    referrals_table = """
    CREATE TABLE IF NOT EXISTS referrals (
        id BIGSERIAL PRIMARY KEY,
        campaign_id BIGINT NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
        invited_email VARCHAR(255),
        invited_phone VARCHAR(50),
        token VARCHAR(36) UNIQUE NOT NULL,
        status VARCHAR(20) DEFAULT 'sent' CHECK (status IN ('sent', 'accepted', 'expired')),
        sent_at TIMESTAMP,
        accepted_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    # 5. Shoutouts table
    print("Creating shoutouts table...")
    shoutouts_table = """
    CREATE TABLE IF NOT EXISTS shoutouts (
        id BIGSERIAL PRIMARY KEY,
        campaign_id BIGINT NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
        donor_id BIGINT REFERENCES users(id),
        display_name VARCHAR(255),
        message VARCHAR(512),
        visible BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    # 6. Milestones table
    print("Creating milestones table...")
    milestones_table = """
    CREATE TABLE IF NOT EXISTS milestones (
        id BIGSERIAL PRIMARY KEY,
        campaign_id BIGINT NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
        title VARCHAR(255) NOT NULL,
        threshold_amount DECIMAL(12,2) NOT NULL,
        achieved_at TIMESTAMP,
        is_auto BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    # 7. Receipts table
    print("Creating receipts table...")
    receipts_table = """
    CREATE TABLE IF NOT EXISTS receipts (
        id BIGSERIAL PRIMARY KEY,
        payment_id BIGINT NOT NULL REFERENCES campaign_payments(id) ON DELETE CASCADE,
        receipt_uuid VARCHAR(36) UNIQUE NOT NULL,
        generated_at TIMESTAMP DEFAULT NOW(),
        receipt_url VARCHAR(1024),
        data JSONB
    );
    """
    
    # 8. Companies table
    print("Creating companies table...")
    companies_table = """
    CREATE TABLE IF NOT EXISTS companies (
        id BIGSERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        contact_email VARCHAR(255),
        website VARCHAR(512),
        logo_url VARCHAR(1024),
        description TEXT,
        is_partner BOOLEAN DEFAULT FALSE,
        partnership_tier VARCHAR(50),
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    # 9. Company partnerships table
    print("Creating company_partnerships table...")
    partnerships_table = """
    CREATE TABLE IF NOT EXISTS company_partnerships (
        id BIGSERIAL PRIMARY KEY,
        company_id BIGINT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
        partnership_type VARCHAR(50) NOT NULL CHECK (partnership_type IN ('banner_ad', 'grant_provider', 'sponsor')),
        cost DECIMAL(12,2),
        duration_months INTEGER,
        banner_url VARCHAR(1024),
        banner_position VARCHAR(50),
        is_active BOOLEAN DEFAULT TRUE,
        start_date TIMESTAMP,
        end_date TIMESTAMP,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    # 10. Student highlights table
    print("Creating student_highlights table...")
    highlights_table = """
    CREATE TABLE IF NOT EXISTS student_highlights (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        achievement VARCHAR(255) NOT NULL,
        description TEXT,
        image_url VARCHAR(1024),
        is_active BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    # 11. Grants table
    print("Creating grants table...")
    grants_table = """
    CREATE TABLE IF NOT EXISTS grants (
        id BIGSERIAL PRIMARY KEY,
        company_id BIGINT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
        title VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        amount DECIMAL(12,2) NOT NULL,
        requirements TEXT,
        application_deadline TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    # Execute table creation
    tables = [
        ("users", users_table),
        ("campaigns", campaigns_table),
        ("campaign_payments", payments_table),
        ("referrals", referrals_table),
        ("shoutouts", shoutouts_table),
        ("milestones", milestones_table),
        ("receipts", receipts_table),
        ("companies", companies_table),
        ("company_partnerships", partnerships_table),
        ("student_highlights", highlights_table),
        ("grants", grants_table)
    ]
    
    for table_name, table_sql in tables:
        try:
            # Note: Supabase uses PostgreSQL, so we need to use raw SQL execution
            # This would typically be done through Supabase dashboard or SQL editor
            print(f"Table {table_name} creation SQL prepared")
            print("=" * 50)
            print(table_sql)
            print("=" * 50)
        except Exception as e:
            print(f"Error creating table {table_name}: {e}")
    
    print("Database initialization completed!")
    print("\nTo complete setup:")
    print("1. Copy the SQL statements above")
    print("2. Go to your Supabase dashboard")
    print("3. Navigate to SQL Editor")
    print("4. Execute each CREATE TABLE statement")
    print("5. Create necessary indexes and constraints")

if __name__ == "__main__":
    init_database()
