# 🗄️ Database Setup Guide

## Quick Fix for RLS Error

The error you're seeing is due to Row Level Security (RLS) being enabled in Supabase without proper policies. Here are two solutions:

### Option 1: Use Development Schema (Recommended for Testing)

1. **Go to your Supabase Dashboard**
2. **Navigate to SQL Editor**
3. **Copy and paste the contents of `database/supabase_schema_dev.sql`**
4. **Execute the SQL**

This version disables RLS for easier development.

### Option 2: Fix RLS Policies (Production Ready)

If you want to keep RLS enabled, update your existing schema with these additional policies:

```sql
-- Add these policies to your existing Supabase project
CREATE POLICY "Users can insert their own profile" ON users FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can insert payments" ON campaign_payments FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can insert referrals" ON referrals FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can insert shoutouts" ON shoutouts FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can insert milestones" ON milestones FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can insert receipts" ON receipts FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can insert companies" ON companies FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can insert partnerships" ON company_partnerships FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can insert highlights" ON student_highlights FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can insert grants" ON grants FOR INSERT WITH CHECK (true);
```

## 🔧 Step-by-Step Setup

### 1. Create Supabase Project
- Go to [supabase.com](https://supabase.com)
- Create a new project
- Wait for it to be ready

### 2. Get Your Credentials
- Go to **Settings** → **API**
- Copy your:
  - Project URL
  - Anon public key
  - Service role key

### 3. Update Your .env File
```env
SUPABASE_URL=your_project_url_here
SUPABASE_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
SECRET_KEY=your_secret_key_here
```

### 4. Run Database Schema
- Go to **SQL Editor** in Supabase
- Copy the contents of `database/supabase_schema_dev.sql`
- Paste and execute

### 5. Test Your Backend
```bash
python test_setup.py
python start_dev.py
```

## 🚨 Common Issues

### RLS Policy Error
**Error**: `new row violates row-level security policy`
**Solution**: Use the development schema or add the missing INSERT policies

### Connection Error
**Error**: `Failed to connect to database`
**Solution**: Check your Supabase credentials in `.env` file

### Authentication Error
**Error**: `Could not validate credentials`
**Solution**: Make sure your `SECRET_KEY` is set in `.env`

## 📋 Verification Checklist

- [ ] Supabase project created
- [ ] Database schema executed
- [ ] Environment variables set
- [ ] Backend starts without errors
- [ ] API documentation accessible at `/docs`

## 🎯 Next Steps

Once your database is set up:
1. Test user registration at `/api/v1/auth/register`
2. Test user login at `/api/v1/auth/login`
3. Create your first campaign
4. Test payment processing

Your fundraising platform will be ready to go! 🚀
