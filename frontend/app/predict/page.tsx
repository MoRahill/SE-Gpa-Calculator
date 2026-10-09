"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/apiClient";
import { PredictionResult } from "@/lib/types";
import PredictionChart from "@/components/PredictionChart";

export default function PredictPage() {
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.predictNextSemester().then(setPrediction).catch((e) => setError(e.message));
  }, []);

  return (
    <div className="container">
      <h1>Predict next semester&apos;s GPA</h1>
      {error && <div className="error">{error}</div>}
      <div className="card">
        {prediction ? <PredictionChart prediction={prediction} /> : <p>Calculating…</p>}
      </div>
    </div>
  );
}
