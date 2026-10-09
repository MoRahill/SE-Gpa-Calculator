import Link from "next/link";

export default function HomePage() {
  return (
    <div className="container">
      <div className="card">
        <h1>Calculate and predict your GPA</h1>
        <p style={{ color: "var(--text-muted)" }}>
          Track your courses, see your current GPA, and get a predicted GPA for next
          semester based on your trend and similar students&apos; outcomes. Advisors can
          review their advisees&apos; progress too.
        </p>
        <div style={{ display: "flex", gap: 10, marginTop: 16 }}>
          <Link className="btn" href="/register">Get started</Link>
          <Link className="btn btn-secondary" href="/login">Log in</Link>
        </div>
      </div>
    </div>
  );
}
