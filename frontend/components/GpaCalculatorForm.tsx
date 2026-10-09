"use client";

import { useState } from "react";
import { api } from "@/lib/apiClient";

const GRADES = ["A+", "A", "B+", "B", "C+", "C", "D+", "D", "F"];

// Starter course catalog - edit this list to match your actual program's courses.
const COURSES = [
  "Calculus I",
  "Calculus II",
  "Introduction to Programming",
  "Data Structures",
  "Discrete Mathematics",
  "Physics I",
  "Physics II",
  "Chemistry",
  "Biology",
  "English Composition",
  "Technical Writing",
  "World History",
  "Microeconomics",
  "Macroeconomics",
  "Statistics",
  "Linear Algebra",
  "Database Systems",
  "Computer Networks",
  "Operating Systems",
  "Software Engineering",
];

const SEMESTER_OPTIONS = Array.from({ length: 12 }, (_, i) => `Semester ${i + 1}`);

export default function GpaCalculatorForm({ onAdded }: { onAdded: () => void }) {
  const [courseName, setCourseName] = useState(COURSES[0]);
  const [creditHours, setCreditHours] = useState("3");
  const [grade, setGrade] = useState("A");
  const [term, setTerm] = useState(SEMESTER_OPTIONS[0]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.addCourse({
        course_name: courseName,
        credit_hours: parseFloat(creditHours),
        grade,
        term,
      });
      onAdded();
    } catch (err: any) {
      setError(err.message || "Could not add course");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1.4fr auto", gap: 10, alignItems: "end" }}>
        <div>
          <label>Course</label>
          <select value={courseName} onChange={(e) => setCourseName(e.target.value)}>
            {COURSES.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div>
          <label>Credits</label>
          <input type="number" step="0.5" min="0.5" value={creditHours} onChange={(e) => setCreditHours(e.target.value)} required />
        </div>
        <div>
          <label>Grade</label>
          <select value={grade} onChange={(e) => setGrade(e.target.value)}>
            {GRADES.map((g) => <option key={g} value={g}>{g}</option>)}
          </select>
        </div>
        <div>
          <label>Semester</label>
          <select value={term} onChange={(e) => setTerm(e.target.value)}>
            {SEMESTER_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <button className="btn" type="submit" disabled={loading} style={{ marginBottom: 12 }}>
          {loading ? "Adding…" : "Add"}
        </button>
      </div>
    </form>
  );
}
