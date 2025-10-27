-- Supabase Database Setup for SafyCore Backend
-- Run these SQL commands in your Supabase SQL Editor
-- https://supabase.com/dashboard/project/_/sql

-- ============================================================
-- 1. CREATE MESSAGES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  session_id VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL CHECK (role IN ('system', 'user', 'assistant')),
  content TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_messages_user_session
  ON messages(user_id, session_id);

CREATE INDEX IF NOT EXISTS idx_messages_created_at
  ON messages(created_at DESC);

-- ============================================================
-- 2. ENABLE ROW LEVEL SECURITY (RLS) FOR MESSAGES
-- ============================================================
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own messages
CREATE POLICY "Users can only access their own messages"
  ON messages
  FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- ============================================================
-- 3. CREATE TRAINING DATA TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS training_data (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  session_id VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_training_data_user_session
  ON training_data(user_id, session_id);

-- ============================================================
-- 4. ENABLE ROW LEVEL SECURITY (RLS) FOR TRAINING DATA
-- ============================================================
ALTER TABLE training_data ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own training data
CREATE POLICY "Users can only access their own training data"
  ON training_data
  FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- ============================================================
-- 5. CREATE FUNCTION TO UPDATE TIMESTAMP
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ============================================================
-- 6. CREATE TRIGGER FOR AUTO-UPDATING TIMESTAMP
-- ============================================================
CREATE TRIGGER update_training_data_updated_at
  BEFORE UPDATE ON training_data
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 7. VERIFY SETUP (Optional - Run to check)
-- ============================================================
-- Check if tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('messages', 'training_data');

-- Check if RLS is enabled
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('messages', 'training_data');

-- Check policies
SELECT tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('messages', 'training_data');

-- ============================================================
-- SETUP COMPLETE!
-- ============================================================
-- Your Supabase database is now configured for SafyCore Backend
--
-- Next steps:
-- 1. Copy your Supabase URL and Keys from:
--    https://supabase.com/dashboard/project/_/settings/api
-- 2. Add them to your .env file in the Django project
-- 3. Run Django migrations: py manage.py migrate
-- 4. Start the Django server: py manage.py runserver
-- ============================================================
