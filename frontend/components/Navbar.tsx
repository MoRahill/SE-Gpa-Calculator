"use client";

import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { getSession, clearSession } from "@/lib/auth";
import { User } from "@/lib/types";

export default function Navbar() {
  const [user, setUser] = useState<User | null>(null);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    setUser(getSession().user);
  }, [pathname]);

  useEffect(() => {
    function handleAuthChange() {
      setUser(getSession().user);
    }
    window.addEventListener("gpa_auth_change", handleAuthChange);
    window.addEventListener("storage", handleAuthChange);
    return () => {
      window.removeEventListener("gpa_auth_change", handleAuthChange);
      window.removeEventListener("storage", handleAuthChange);
    };
  }, []);

  function handleLogout() {
    clearSession();
    setUser(null);
    router.push("/login");
  }

  return (
    <div style={{ borderBottom: "1px solid var(--border)", background: "var(--card)" }}>
      <div className="container" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 20px" }}>
        <Link href="/" style={{ fontWeight: 600, color: "var(--text)" }}>GPA Calculator</Link>
        <div style={{ display: "flex", gap: 18, alignItems: "center", fontSize: 14 }}>
          {user ? (
            <>
              {user.role === "student" && (
                <>
                  <Link href="/dashboard">Dashboard</Link>
                  <Link href="/gpa">GPA</Link>
                  <Link href="/predict">Predict</Link>
                </>
              )}
              {user.role === "advisor" && <Link href="/advisor">Advisees</Link>}
              <button className="btn btn-secondary" onClick={handleLogout}>Log out</button>
            </>
          ) : (
            <>
              <Link href="/login">Log in</Link>
              <Link href="/register">Register</Link>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
