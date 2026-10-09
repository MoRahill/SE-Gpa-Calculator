# GPA Calculator

A full-stack app for students to track grades, calculate GPA, and get a
predicted GPA for next semester - with advisor accounts that can review
their advisees' progress, degree completion estimates, GPA trend charts,
and export PDF reports.

**Stack:** Next.js (React/TypeScript) frontend · FastAPI (Python) backend ·
PostgreSQL + pgvector for similarity-based GPA prediction · matplotlib for
charts · reportlab for PDF export.

## Running locally (Docker)

```bash
cd infra
docker compose up --build
```
- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs

The schema applies automatically on a **first run** (empty DB volume) via
`database/schema.sql`. If you already have a running database from before
and are just picking up this update, run the incremental migration instead:
```bash
docker compose exec db psql -U postgres -d gpa_calculator -f /dev/stdin < ../database/migrations/0002_add_year_and_credits_required.sql
```

## Running locally without Docker

**Backend**
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit with your DB URL / secret
uvicorn app.main:app --reload
```
Needs a Postgres database with the `vector` extension (a free
[Supabase](https://supabase.com) project works well). Apply
`database/schema.sql` to it.

**Frontend**
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

## Running tests
```bash
cd backend
python -m pytest tests/ -v
```

## What's new: advisor features

- **Advisee dashboard** (`/advisor`): each student shown as a clickable
  card with name, year, and cumulative GPA.
- **Advisee detail page** (`/advisor/[studentId]`): full course history
  grouped by semester, a degree-progress summary (credits/courses/semesters
  remaining, estimated from the student's own pace - not an official
  degree audit), a matplotlib-generated GPA trend chart, and a one-click
  **PDF export** of the whole report.
- **Students see their advisor's name** on their dashboard once assigned.

Assigning a student to an advisor still requires a manual database update
(no UI for this yet):
```sql
UPDATE users SET advisor_id = '<advisor-uuid>' WHERE id = '<student-uuid>';
```

## Project structure
```
gpa-calculator/
├── frontend/        Next.js app (UI)
├── backend/          FastAPI app (API, auth, GPA logic, prediction, charts, PDF export)
├── database/          Postgres schema + migrations
├── infra/              docker-compose.yml for local dev
└── .github/workflows/  CI pipeline
```

## Deploying
- **Frontend** → Vercel, root directory `frontend/`, env var `NEXT_PUBLIC_API_URL`.
- **Backend** → Railway/Render, root directory `backend/`, env vars
  `DATABASE_URL`, `JWT_SECRET_KEY`, `FRONTEND_ORIGIN`.
- **Database** → your Supabase project (pgvector already enabled).
