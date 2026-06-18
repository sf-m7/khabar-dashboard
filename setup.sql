-- =============================================================
-- Khabar dashboard — users table
-- Run this once in your Supabase SQL editor.
-- The first user account is created via the app itself
-- (the first visit shows a "Create account" form automatically).
-- =============================================================

CREATE TABLE IF NOT EXISTS public.dashboard_users (
  username        TEXT PRIMARY KEY,
  password_hash   TEXT NOT NULL,
  full_name       TEXT,
  company         TEXT,
  tier            TEXT DEFAULT 'basic',         -- 'basic' | 'pro' | 'enterprise'
  categories      JSONB DEFAULT '[]'::jsonb,
  brand_tier      TEXT,                          -- 'mass-market' | 'mid-range' | etc
  gender_focus    TEXT,                          -- 'men' | 'women' | 'both' | 'kids'
  watch_list      JSONB DEFAULT '[]'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  last_login      TIMESTAMPTZ
);
