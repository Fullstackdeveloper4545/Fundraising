-- Quick fix for the referral_count and pending_approval status issue
-- Run this in your Supabase SQL Editor

-- Add referral_count column if it doesn't exist
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS referral_count INTEGER DEFAULT 0;

-- Update the status constraint to include pending_approval
ALTER TABLE campaigns DROP CONSTRAINT IF EXISTS campaigns_status_check;
ALTER TABLE campaigns ADD CONSTRAINT campaigns_status_check 
    CHECK (status IN ('draft', 'pending_approval', 'active', 'paused', 'completed', 'cancelled', 'expired'));

-- Set referral_count to 0 for existing campaigns
UPDATE campaigns SET referral_count = 0 WHERE referral_count IS NULL;

-- Verify the changes
SELECT id, title, status, referral_count FROM campaigns LIMIT 5;
