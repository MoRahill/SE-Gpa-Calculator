"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/apiClient";
import { GpaSummary, User } from "@/lib/types";

export default function DashboardPage() {
  const [summary, setSummary] = useState<GpaSummary | null>(null);
  const [me, setMe] = useState<User | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getGpaSummary().then(setSummary).catch((e) => setError(e.message));
    api.me().then(setMe).catch(() => {});
  }, []);

  return (
    <div className="container">
      <h1>Dashboard</h1>
      {error && <div className="error">{error}</div>}

      {me?.role === "student" && (
        <div className="card">
          {me.advisor_name ? (
            <p style={{ margin: 0 }}>
              Your advisor: <strong>{me.advisor_name}</strong>
            </p>
          ) : (
            <p style={{ margin: 0, color: "var(--text-muted)" }}>
              No advisor assigned yet.
            </p>
          )}
        </div>
      )}

      <div className="card">
        {summary ? (
          <>
            <div className="stat">
              <div className="value">{summary.cumulative_gpa.toFixed(2)}</div>
              <div className="label">Cumulative GPA</div>
            </div>
            <div className="stat">
              <div className="value">{summary.term_gpa.toFixed(2)}</div>
              <div className="label">Most recent semester GPA</div>
            </div>
            <div className="stat">
              <div className="value">{summary.total_credit_hours}</div>
              <div className="label">Total credit hours</div>
            </div>
          </>
        ) : (
          <p>Loading…</p>
        )}
      </div>

      <div className="card">
        <Link className="btn" href="/gpa">Manage courses & GPA</Link>{" "}
        <Link className="btn btn-secondary" href="/predict">Predict next semester</Link>
      </div>
    </div>
  );
}
