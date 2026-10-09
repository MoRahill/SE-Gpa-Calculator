"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import { api } from "@/lib/apiClient";
import { GpaSummary, Course } from "@/lib/types";
import GpaCalculatorForm from "@/components/GpaCalculatorForm";
import CourseTable from "@/components/CourseTable";

function semesterNumber(term: string): number {
  const match = term.match(/\d+/);
  return match ? parseInt(match[0], 10) : 0;
}

function calcGroupGpa(courses: Course[]): number {
  const totalCredits = courses.reduce((sum, c) => sum + c.credit_hours, 0);
  if (totalCredits === 0) return 0;
  const totalPoints = courses.reduce((sum, c) => sum + c.grade_points * c.credit_hours, 0);
  return Math.round((totalPoints / totalCredits) * 100) / 100;
}

export default function GpaPage() {
  const [summary, setSummary] = useState<GpaSummary | null>(null);
  const [error, setError] = useState("");

  const load = useCallback(() => {
    api.getGpaSummary().then(setSummary).catch((e) => setError(e.message));
  }, []);

  useEffect(() => { load(); }, [load]);

  async function handleDelete(id: string) {
    try {
      await api.deleteCourse(id);
      load();
    } catch (e: any) {
      setError(e.message);
    }
  }

  const semesterGroups = useMemo(() => {
    if (!summary) return [];
    const groups = new Map<string, Course[]>();
    for (const course of summary.courses) {
      const list = groups.get(course.term) || [];
      list.push(course);
      groups.set(course.term, list);
    }
    return Array.from(groups.entries())
      .map(([term, courses]) => ({ term, courses, gpa: calcGroupGpa(courses) }))
      .sort((a, b) => semesterNumber(a.term) - semesterNumber(b.term));
  }, [summary]);

  return (
    <div className="container">
      <h1>GPA calculator</h1>
      <p style={{ color: "var(--text-muted)", marginTop: -8 }}>
        This calculator uses a 4.0 scale, where A+ is 4.0, A is 3.75, B+ is 3.5, and so on.
      </p>
      {error && <div className="error">{error}</div>}

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Add a course</h3>
        <GpaCalculatorForm onAdded={load} />
      </div>

      {summary && (
        <div className="card">
          <div className="stat">
            <div className="value">{summary.cumulative_gpa.toFixed(2)}</div>
            <div className="label">Cumulative GPA (all semesters)</div>
          </div>
          <div className="stat">
            <div className="value">{summary.total_credit_hours}</div>
            <div className="label">Total credit hours</div>
          </div>
        </div>
      )}

      {semesterGroups.length === 0 && (
        <div className="card">
          <p style={{ color: "var(--text-muted)", margin: 0 }}>No courses added yet.</p>
        </div>
      )}

      {semesterGroups.map(({ term, courses, gpa }) => (
        <div className="card" key={term}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
            <h3 style={{ margin: 0 }}>{term}</h3>
            <div className="stat" style={{ margin: 0 }}>
              <div className="value" style={{ fontSize: 20 }}>{gpa.toFixed(2)}</div>
              <div className="label">GPA</div>
            </div>
          </div>
          <CourseTable courses={courses} onDelete={handleDelete} />
        </div>
      ))}
    </div>
  );
}
