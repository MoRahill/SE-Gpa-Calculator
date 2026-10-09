"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/apiClient";
import { AdviseeDetail } from "@/lib/types";

export default function AdviseeDetailPage({ params }: { params: { studentId: string } }) {
  const [detail, setDetail] = useState<AdviseeDetail | null>(null);
  const [chartUrl, setChartUrl] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    api.getAdviseeDetail(params.studentId).then(setDetail).catch((e) => setError(e.message));

    // The chart endpoint requires an Authorization header, which a plain
    // <img src="..."> can't send - so we fetch it as a blob and turn that
    // into an object URL the <img> tag can display.
    let objectUrl: string | null = null;
    api.getAdviseeChartBlob(params.studentId).then((blob) => {
      objectUrl = URL.createObjectURL(blob);
      setChartUrl(objectUrl);
    }).catch(() => {});

    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [params.studentId]);

  async function handleExport() {
    setExporting(true);
    try {
      const blob = await api.exportAdviseeReportBlob(params.studentId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${detail?.full_name.replace(/\s+/g, "_") || "student"}_report.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e: any) {
      setError(e.message || "Could not export report");
    } finally {
      setExporting(false);
    }
  }

  if (error) return <div className="container"><div className="error">{error}</div></div>;
  if (!detail) return <div className="container">Loading…</div>;

  const dp = detail.degree_progress;

  return (
    <div className="container">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 style={{ marginBottom: 2 }}>{detail.full_name}</h1>
          <p style={{ color: "var(--text-muted)", marginTop: 0 }}>{detail.email}</p>
        </div>
        <button className="btn" onClick={handleExport} disabled={exporting}>
          {exporting ? "Exporting…" : "Export PDF report"}
        </button>
      </div>

      <div className="card">
        <div className="stat">
          <div className="value">{detail.cumulative_gpa.toFixed(2)}</div>
          <div className="label">Cumulative GPA</div>
        </div>
        <div className="stat">
          <div className="value">{dp.credits_completed}</div>
          <div className="label">Credits completed</div>
        </div>
        <div className="stat">
          <div className="value">{dp.credits_remaining}</div>
          <div className="label">Credits left (of {dp.credits_required})</div>
        </div>
        <div className="stat">
          <div className="value">{dp.courses_remaining_estimate ?? "—"}</div>
          <div className="label">Est. courses remaining</div>
        </div>
        <div className="stat">
          <div className="value">{dp.semesters_remaining_estimate ?? "—"}</div>
          <div className="label">Est. semesters remaining</div>
        </div>
        <p style={{ color: "var(--text-muted)", fontSize: 12, marginTop: 10, marginBottom: 0 }}>
          Remaining estimates are based on this student&apos;s average pace so far - not an official degree audit.
        </p>
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>GPA trend</h3>
        {chartUrl ? (
          <img src={chartUrl} alt="GPA trend chart" style={{ maxWidth: "100%", borderRadius: 6 }} />
        ) : (
          <p style={{ color: "var(--text-muted)" }}>Loading chart…</p>
        )}
      </div>

      {detail.semesters.length === 0 && (
        <div className="card">
          <p style={{ color: "var(--text-muted)", margin: 0 }}>No courses recorded yet.</p>
        </div>
      )}

      {detail.semesters.map((sem) => (
        <div className="card" key={sem.term}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
            <h3 style={{ margin: 0 }}>{sem.term}</h3>
            <div className="stat" style={{ margin: 0 }}>
              <div className="value" style={{ fontSize: 20 }}>{sem.gpa.toFixed(2)}</div>
              <div className="label">GPA</div>
            </div>
          </div>
          <table>
            <thead>
              <tr><th>Course</th><th>Credits</th><th>Grade</th></tr>
            </thead>
            <tbody>
              {sem.courses.map((c, i) => (
                <tr key={i}>
                  <td>{c.course_name}</td>
                  <td>{c.credit_hours}</td>
                  <td>{c.grade}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}
