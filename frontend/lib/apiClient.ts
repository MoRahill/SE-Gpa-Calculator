const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("gpa_token");
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: HeadersInit = {
    ...(options.body && !(options.body instanceof URLSearchParams) ? { "Content-Type": "application/json" } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorBody.detail || "Request failed");
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

/** For endpoints that return a binary file (chart image, PDF export).
 * These can't be loaded with a plain <img src="..."> or <a href="...">
 * because the browser won't attach the Authorization header to those -
 * so we fetch them as a blob here and the caller turns that into an
 * object URL instead. */
async function requestBlob(path: string): Promise<Blob> {
  const token = getToken();
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) {
    throw new Error(`Request failed (${res.status})`);
  }
  return res.blob();
}

export const api = {
  register: (data: { email: string; password: string; full_name: string; role: string; year?: number; total_credits_required?: number }) =>
    request<{ access_token: string; user: any }>("/users/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  login: (email: string, password: string) => {
    const form = new URLSearchParams();
    form.set("username", email);
    form.set("password", password);
    return request<{ access_token: string; user: any }>("/users/login", {
      method: "POST",
      body: form,
    });
  },

  me: () => request<import("./types").User>("/users/me"),

  getGpaSummary: (term?: string) =>
    request<import("./types").GpaSummary>(`/gpa/summary${term ? `?term=${encodeURIComponent(term)}` : ""}`),

  addCourse: (data: { course_name: string; credit_hours: number; grade: string; term: string }) =>
    request<import("./types").Course>("/gpa/courses", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  deleteCourse: (courseId: string) =>
    request<void>(`/gpa/courses/${courseId}`, { method: "DELETE" }),

  predictNextSemester: () =>
    request<import("./types").PredictionResult>("/predict/next-semester"),

  getAdvisees: () =>
    request<import("./types").AdviseeSummary[]>("/advisor/advisees"),

  getAdviseeDetail: (studentId: string) =>
    request<import("./types").AdviseeDetail>(`/advisor/advisees/${studentId}`),

  getAdviseeChartBlob: (studentId: string) =>
    requestBlob(`/advisor/advisees/${studentId}/chart.png`),

  exportAdviseeReportBlob: (studentId: string) =>
    requestBlob(`/advisor/advisees/${studentId}/export.pdf`),
};
