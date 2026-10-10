"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/apiClient";
import { saveSession } from "@/lib/auth";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("student");
  const [year, setYear] = useState("1");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const result = await api.register({
        email,
        password,
        full_name: fullName,
        role,
        ...(role === "student" ? { year: parseInt(year, 10) } : {}),
      });
      saveSession(result.access_token, result.user);
      router.push(result.user.role === "advisor" ? "/advisor" : "/dashboard");
    } catch (err: any) {
      setError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container" style={{ maxWidth: 420 }}>
      <div className="card">
        <h2>Create an account</h2>
        <form onSubmit={handleSubmit}>
          {error && <div className="error">{error}</div>}
          <label>Full name</label>
          <input value={fullName} onChange={(e) => setFullName(e.target.value)} required />
          <label>Email</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <label>Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
          <label>I am a</label>
          <select value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="student">Student</option>
            <option value="advisor">Advisor</option>
          </select>
          {role === "student" && (
            <>
              <label>Year</label>
              <select value={year} onChange={(e) => setYear(e.target.value)}>
                <option value="1">1st year</option>
                <option value="2">2nd year</option>
                <option value="3">3rd year</option>
                <option value="4">4th year</option>
                <option value="5">5th year</option>
                <option value="6">6th year</option>
              </select>
            </>
          )}
          <button className="btn" type="submit" disabled={loading} style={{ width: "100%" }}>
            {loading ? "Creating account…" : "Register"}
          </button>
        </form>
      </div>
    </div>
  );
}
