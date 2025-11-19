-- Disable RLS for student_highlights table (for development only)
-- Run this in your Supabase SQL Editor

-- Disable RLS temporarily for easier development
ALTER TABLE student_highlights DISABLE ROW LEVEL SECURITY;

-- Alternative: If you want to keep RLS enabled but make it permissive
-- DROP POLICY IF EXISTS "Users can insert highlights" ON student_highlights;
-- CREATE POLICY "Allow all operations on highlights" ON student_highlights 
-- FOR ALL USING (true) WITH CHECK (true);
