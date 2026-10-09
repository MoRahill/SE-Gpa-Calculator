-- GPA Calculator database schema (PostgreSQL + pgvector)

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('student', 'advisor')) DEFAULT 'student',
    advisor_id UUID REFERENCES users(id) ON DELETE SET NULL, -- which advisor this student is assigned to
    year INTEGER CHECK (year BETWEEN 1 AND 6),                -- class year, for students
    total_credits_required NUMERIC(6,2) NOT NULL DEFAULT 120, -- credits needed to graduate, for students
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_name TEXT NOT NULL,
    credit_hours NUMERIC(4,2) NOT NULL CHECK (credit_hours > 0),
    grade TEXT NOT NULL,
    grade_points NUMERIC(3,2) NOT NULL,
    term TEXT NOT NULL,               -- e.g. 'Semester 1'
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS gpa_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    term TEXT NOT NULL,
    term_gpa NUMERIC(3,2) NOT NULL,
    cumulative_gpa NUMERIC(3,2) NOT NULL,
    total_credit_hours NUMERIC(6,2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, term)
);

-- Student academic-profile embeddings, used for similarity-based GPA prediction.
CREATE TABLE IF NOT EXISTS student_embeddings (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    embedding vector(16) NOT NULL,
    final_gpa NUMERIC(3,2),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_student_embeddings_vector
    ON student_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);

CREATE INDEX IF NOT EXISTS idx_courses_user_id ON courses(user_id);
CREATE INDEX IF NOT EXISTS idx_gpa_snapshots_user_id ON gpa_snapshots(user_id);
CREATE INDEX IF NOT EXISTS idx_users_advisor_id ON users(advisor_id);
