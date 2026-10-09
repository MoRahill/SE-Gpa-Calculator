"use client";

import { PredictionResult } from "@/lib/types";

export default function PredictionChart({ prediction }: { prediction: PredictionResult }) {
  const pct = Math.min(100, (prediction.predicted_gpa / 4.0) * 100);

  return (
    <div>
      <div className="stat">
        <div className="value">{prediction.predicted_gpa.toFixed(2)}</div>
        <div className="label">Predicted next-semester GPA</div>
      </div>

      <div style={{ background: "var(--border)", borderRadius: 6, height: 10, marginTop: 14, overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, background: "var(--accent)", height: "100%" }} />
      </div>

      <p style={{ color: "var(--text-muted)", fontSize: 13, marginTop: 14 }}>
        {prediction.note}
      </p>
    </div>
  );
}
