-- Migration to add referral_count field and pending_approval status
-- Execute this in your Supabase SQL Editor

-- Add referral_count column to campaigns table
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS referral_count INTEGER DEFAULT 0;

-- Update the status check constraint to include pending_approval
ALTER TABLE campaigns DROP CONSTRAINT IF EXISTS campaigns_status_check;
ALTER TABLE campaigns ADD CONSTRAINT campaigns_status_check 
    CHECK (status IN ('draft', 'pending_approval', 'active', 'paused', 'completed', 'cancelled', 'expired'));

-- Update existing campaigns to have referral_count = 0 if NULL
UPDATE campaigns SET referral_count = 0 WHERE referral_count IS NULL;
