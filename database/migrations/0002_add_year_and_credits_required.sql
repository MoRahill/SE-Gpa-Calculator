-- Migration 0002: adds class year and degree credit requirement to users.
-- Run this against an EXISTING database that was created before this migration
-- (schema.sql only auto-applies to a brand-new database volume).
--
-- Via docker compose:
--   docker compose exec db psql -U postgres -d gpa_calculator -f /dev/stdin < database/migrations/0002_add_year_and_credits_required.sql

ALTER TABLE users ADD COLUMN IF NOT EXISTS year INTEGER CHECK (year BETWEEN 1 AND 6);
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_credits_required NUMERIC(6,2) NOT NULL DEFAULT 120;
CREATE INDEX IF NOT EXISTS idx_users_advisor_id ON users(advisor_id);
