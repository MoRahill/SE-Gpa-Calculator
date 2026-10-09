"use client";

import { useRouter } from "next/navigation";
import { AdviseeSummary } from "@/lib/types";

function yearLabel(year: number | null): string {
  if (!year) return "Year not set";
  const suffixes: Record<number, string> = { 1: "1st", 2: "2nd", 3: "3rd" };
  return `${suffixes[year] || `${year}th`} year`;
}

export default function AdviseeList({ advisees }: { advisees: AdviseeSummary[] }) {
  const router = useRouter();

  if (advisees.length === 0) {
    return <p style={{ color: "var(--text-muted)" }}>No advisees assigned yet.</p>;
  }

  return (
    <div className="advisee-grid">
      {advisees.map((a) => (
        <div
          key={a.id}
          className="advisee-block"
          onClick={() => router.push(`/advisor/${a.id}`)}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => { if (e.key === "Enter") router.push(`/advisor/${a.id}`); }}
        >
          <div className="name">{a.full_name}</div>
          <div className="meta">{yearLabel(a.year)} &middot; {a.email}</div>
          <div className="gpa-value">{a.cumulative_gpa.toFixed(2)}</div>
          <div className="gpa-label">Cumulative GPA</div>
        </div>
      ))}
    </div>
  );
}
