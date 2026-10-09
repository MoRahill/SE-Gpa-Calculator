"use client";

import { Course } from "@/lib/types";

export default function CourseTable({
  courses,
  onDelete,
}: {
  courses: Course[];
  onDelete?: (id: string) => void;
}) {
  if (courses.length === 0) {
    return <p style={{ color: "var(--text-muted)" }}>No courses added yet.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Course</th>
          <th>Term</th>
          <th>Credits</th>
          <th>Grade</th>
          {onDelete && <th></th>}
        </tr>
      </thead>
      <tbody>
        {courses.map((c) => (
          <tr key={c.id}>
            <td>{c.course_name}</td>
            <td>{c.term}</td>
            <td>{c.credit_hours}</td>
            <td>{c.grade}</td>
            {onDelete && (
              <td>
                <button className="btn btn-secondary" style={{ padding: "4px 10px", fontSize: 12 }} onClick={() => onDelete(c.id)}>
                  Remove
                </button>
              </td>
            )}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
