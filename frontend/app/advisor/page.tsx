"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/apiClient";
import { AdviseeSummary } from "@/lib/types";
import AdviseeList from "@/components/AdviseeList";

export default function AdvisorPage() {
  const [advisees, setAdvisees] = useState<AdviseeSummary[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getAdvisees().then(setAdvisees).catch((e) => setError(e.message));
  }, []);

  return (
    <div className="container">
      <h1>Your advisees</h1>
      <p style={{ color: "var(--text-muted)", marginTop: -8 }}>
        Click on a student to see their full course history, degree progress, and GPA trend.
      </p>
      {error && <div className="error">{error}</div>}
      <AdviseeList advisees={advisees} />
    </div>
  );
}
