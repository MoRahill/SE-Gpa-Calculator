export interface User {
  id: string;
  email: string;
  full_name: string;
  role: "student" | "advisor";
  year: number | null;
  total_credits_required: number;
  advisor_name: string | null;
}

export interface Course {
  id: string;
  course_name: string;
  credit_hours: number;
  grade: string;
  grade_points: number;
  term: string;
}

export interface GpaSummary {
  courses: Course[];
  term_gpa: number;
  cumulative_gpa: number;
  total_credit_hours: number;
}

export interface PredictionResult {
  predicted_gpa: number;
  method: string;
  note: string;
  similar_student_count: number;
}

export interface AdviseeSummary {
  id: string;
  full_name: string;
  email: string;
  year: number | null;
  cumulative_gpa: number;
}

export interface DegreeProgress {
  credits_completed: number;
  credits_required: number;
  credits_remaining: number;
  courses_remaining_estimate: number | null;
  semesters_remaining_estimate: number | null;
}

export interface SemesterBreakdown {
  term: string;
  gpa: number;
  courses: Array<{
    course_name: string;
    grade: string;
    grade_points: number;
    credit_hours: number;
    term: string;
  }>;
}

export interface AdviseeDetail {
  id: string;
  full_name: string;
  email: string;
  year: number | null;
  cumulative_gpa: number;
  degree_progress: DegreeProgress;
  semesters: SemesterBreakdown[];
}
