-- Fix RLS policies for student_highlights table
-- Run this in your Supabase SQL Editor

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can insert highlights" ON student_highlights;
DROP POLICY IF EXISTS "Users can view highlights" ON student_highlights;
DROP POLICY IF EXISTS "Users can update highlights" ON student_highlights;

-- Create comprehensive policies for student_highlights
-- Allow anyone to insert highlights (for admin operations)
CREATE POLICY "Allow insert highlights" ON student_highlights 
FOR INSERT WITH CHECK (true);

-- Allow anyone to view highlights (public data)
CREATE POLICY "Allow view highlights" ON student_highlights 
FOR SELECT USING (true);

-- Allow updates for admin operations
CREATE POLICY "Allow update highlights" ON student_highlights 
FOR UPDATE USING (true);

-- Allow deletes for admin operations
CREATE POLICY "Allow delete highlights" ON student_highlights 
FOR DELETE USING (true);
